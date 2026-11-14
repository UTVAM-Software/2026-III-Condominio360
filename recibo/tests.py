from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from aportacion.models import Aportacion
from usuario.forms import asignar_rol

from .models import PagoPayPal, Recibo

CLAVE = 'Prueba12345'
CONFIG = dict(PAYPAL_CLIENT_ID='id-prueba', PAYPAL_CLIENT_SECRET='secreto-prueba', PAYPAL_CURRENCY='MXN')


def respuesta_captura(valor='1200.00', moneda='MXN', estado='COMPLETED'):
    return {'status': 'COMPLETED', 'purchase_units': [{'payments': {'captures': [
        {'id': 'CAP123', 'status': estado, 'amount': {'value': valor, 'currency_code': moneda}}]}}]}


@override_settings(**CONFIG)
class PayPalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.r1 = User.objects.create_user('r1', password=CLAVE)
        cls.r2 = User.objects.create_user('r2', password=CLAVE)
        for u in (cls.r1, cls.r2):
            asignar_rol(u, 'Residente')
        cls.ap1 = Aportacion.objects.create(residente=cls.r1, monto=Decimal('1200.00'),
                                            fecha_limite=date(2026, 1, 1))
        cls.ap2 = Aportacion.objects.create(residente=cls.r2, monto=Decimal('1200.00'),
                                            fecha_limite=date(2026, 1, 1))

    def iniciar(self, ap):
        with patch('recibo.paypal.crear_orden',
                   return_value=('ORDEN12345', 'https://www.sandbox.paypal.com/checkoutnow?token=ORDEN12345')):
            return self.client.post(reverse('recibo:paypal_iniciar', args=[ap.pk]))

    def test_residente_inicia_pago_de_su_aportacion(self):
        self.client.login(username='r1', password=CLAVE)
        r = self.iniciar(self.ap1)
        self.assertEqual(r.status_code, 302)
        self.assertIn('paypal.com', r['Location'])
        self.assertEqual(PagoPayPal.objects.get().monto, Decimal('1200.00'))

    def test_no_puede_pagar_aportacion_ajena(self):
        self.client.login(username='r1', password=CLAVE)
        self.assertEqual(self.iniciar(self.ap2).status_code, 404)
        self.assertFalse(PagoPayPal.objects.exists())

    def test_iniciar_exige_post_y_sesion(self):
        url = reverse('recibo:paypal_iniciar', args=[self.ap1.pk])
        self.assertEqual(self.client.post(url).status_code, 302)  # sin sesión -> login
        self.client.login(username='r1', password=CLAVE)
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_retorno_completo_crea_recibo(self):
        self.client.login(username='r1', password=CLAVE)
        self.iniciar(self.ap1)
        with patch('recibo.paypal.capturar_orden', return_value=respuesta_captura()):
            r = self.client.get(reverse('recibo:paypal_retorno'), {'token': 'ORDEN12345'})
        self.assertEqual(r.status_code, 302)
        self.ap1.refresh_from_db()
        self.assertTrue(self.ap1.pagada)
        self.assertEqual(Recibo.objects.get().metodo, 'PayPal')
        self.assertEqual(PagoPayPal.objects.get().estado, 'COMPLETADO')

    def test_recargar_retorno_no_cobra_dos_veces(self):
        self.client.login(username='r1', password=CLAVE)
        self.iniciar(self.ap1)
        with patch('recibo.paypal.capturar_orden', return_value=respuesta_captura()) as cap:
            self.client.get(reverse('recibo:paypal_retorno'), {'token': 'ORDEN12345'})
            self.client.get(reverse('recibo:paypal_retorno'), {'token': 'ORDEN12345'})
        self.assertEqual(cap.call_count, 1)
        self.assertEqual(Recibo.objects.count(), 1)

    def test_monto_distinto_no_registra_pago(self):
        self.client.login(username='r1', password=CLAVE)
        self.iniciar(self.ap1)
        with patch('recibo.paypal.capturar_orden', return_value=respuesta_captura(valor='1.00')):
            self.client.get(reverse('recibo:paypal_retorno'), {'token': 'ORDEN12345'})
        self.ap1.refresh_from_db()
        self.assertFalse(self.ap1.pagada)
        self.assertFalse(Recibo.objects.exists())
        self.assertEqual(PagoPayPal.objects.get().estado, 'FALLIDO')

    def test_otro_usuario_no_puede_usar_la_orden(self):
        self.client.login(username='r1', password=CLAVE)
        self.iniciar(self.ap1)
        self.client.logout()
        self.client.login(username='r2', password=CLAVE)
        r = self.client.get(reverse('recibo:paypal_retorno'), {'token': 'ORDEN12345'})
        self.assertEqual(r.status_code, 404)

    def test_modo_lectura_sigue_bloqueando_otras_modificaciones(self):
        self.client.login(username='r1', password=CLAVE)
        r = self.client.post(reverse('aportacion:eliminar', args=[self.ap1.pk]))
        self.assertEqual(r.status_code, 403)

    def test_cancelar_marca_cancelado(self):
        self.client.login(username='r1', password=CLAVE)
        self.iniciar(self.ap1)
        self.client.get(reverse('recibo:paypal_cancelado'), {'token': 'ORDEN12345'})
        self.assertEqual(PagoPayPal.objects.get().estado, 'CANCELADO')
