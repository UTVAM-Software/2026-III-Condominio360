"""Cliente mínimo de PayPal Orders v2 (flujo con redirección).

Flujo: crear orden -> el residente aprueba en PayPal -> el servidor captura.
Usa solo la librería estándar, así no hay que instalar paquetes.
"""
import base64
import json
import re
import urllib.error
import urllib.request
import uuid
from urllib.parse import urlparse

from django.conf import settings


class PayPalError(Exception):
    pass


def configurado():
    return bool(settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET)


def _base():
    if settings.PAYPAL_MODE == 'live':
        return 'https://api-m.paypal.com'
    return 'https://api-m.sandbox.paypal.com'


def _peticion(metodo, ruta, datos=None, headers=None, cuerpo_bruto=None):
    h = {'Accept': 'application/json'}
    h.update(headers or {})
    cuerpo = None
    if cuerpo_bruto is not None:
        cuerpo = cuerpo_bruto
    elif datos is not None:
        cuerpo = json.dumps(datos).encode('utf-8')
        h['Content-Type'] = 'application/json'
    req = urllib.request.Request(_base() + ruta, data=cuerpo, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode('utf-8') or '{}')
    except urllib.error.HTTPError as e:
        detalle = e.read().decode('utf-8', errors='replace')[:400]
        raise PayPalError(f'PayPal respondió {e.code}: {detalle}') from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise PayPalError(f'No se pudo conectar con PayPal: {e}') from e


def _token():
    credenciales = f'{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}'
    cred = base64.b64encode(credenciales.encode('utf-8')).decode('ascii')
    r = _peticion(
        'POST', '/v1/oauth2/token',
        headers={'Authorization': f'Basic {cred}',
                 'Content-Type': 'application/x-www-form-urlencoded'},
        cuerpo_bruto=b'grant_type=client_credentials',
    )
    try:
        return r['access_token']
    except KeyError as e:
        raise PayPalError('PayPal no devolvió access_token') from e


def crear_orden(monto, moneda, referencia, descripcion, return_url, cancel_url):
    """Crea la orden y devuelve (order_id, url_de_aprobacion).

    El monto SIEMPRE viene de la base de datos, nunca del navegador.
    """
    datos = {
        'intent': 'CAPTURE',
        'purchase_units': [{
            'reference_id': str(referencia)[:127],
            'description': descripcion[:127],
            'amount': {'currency_code': moneda, 'value': f'{monto:.2f}'},
        }],
        'payment_source': {'paypal': {'experience_context': {
            'brand_name': 'Condominio360',
            'locale': 'es-MX',
            'landing_page': 'LOGIN',
            'shipping_preference': 'NO_SHIPPING',
            'user_action': 'PAY_NOW',
            'return_url': return_url,
            'cancel_url': cancel_url,
        }}},
    }
    resp = _peticion(
        'POST', '/v2/checkout/orders', datos,
        {'Authorization': f'Bearer {_token()}', 'PayPal-Request-Id': str(uuid.uuid4())},
    )
    url = next((l.get('href') for l in resp.get('links', [])
                if l.get('rel') in ('payer-action', 'approve')), None)
    if not resp.get('id') or not url:
        raise PayPalError('PayPal no devolvió la orden o el enlace de aprobación')
    host = urlparse(url).hostname or ''
    if not (url.startswith('https://') and host.endswith('paypal.com')):
        raise PayPalError('Enlace de aprobación no confiable')
    return resp['id'], url


def capturar_orden(order_id):
    if not re.fullmatch(r'[A-Za-z0-9_-]{5,64}', order_id or ''):
        raise PayPalError('Identificador de orden inválido')
    return _peticion(
        'POST', f'/v2/checkout/orders/{order_id}/capture', {},
        {'Authorization': f'Bearer {_token()}', 'PayPal-Request-Id': f'cap-{order_id}'},
    )


def extraer_captura(resp):
    try:
        cap = resp['purchase_units'][0]['payments']['captures'][0]
        return {'id': cap['id'], 'status': cap['status'],
                'value': cap['amount']['value'], 'currency': cap['amount']['currency_code']}
    except (KeyError, IndexError, TypeError) as e:
        raise PayPalError('Respuesta de captura inesperada') from e
