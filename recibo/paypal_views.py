import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from aportacion.models import Aportacion

from . import paypal
from .models import PagoPayPal, Recibo

log = logging.getLogger(__name__)


@login_required
@require_POST
def paypal_iniciar(request, aportacion_id):
    """El residente inicia el pago de SU aportación pendiente.

    - Solo la dueña/el dueño de la aportación (si es de otra persona: 404).
    - El monto sale de la base de datos, no del formulario.
    """
    ap = get_object_or_404(Aportacion, pk=aportacion_id, residente=request.user, pagada=False)

    if not paypal.configurado():
        messages.error(request, 'El pago en línea aún no está configurado. '
                                'Paga por transferencia y la administración registrará tu pago.')
        return redirect('pagos')

    try:
        order_id, url = paypal.crear_orden(
            monto=ap.monto,
            moneda=settings.PAYPAL_CURRENCY,
            referencia=f'aportacion-{ap.pk}',
            descripcion=ap.concepto,
            return_url=request.build_absolute_uri(reverse('recibo:paypal_retorno')),
            cancel_url=request.build_absolute_uri(reverse('recibo:paypal_cancelado')),
        )
    except paypal.PayPalError:
        log.exception('No se pudo crear la orden de PayPal')
        messages.error(request, 'No se pudo iniciar el pago con PayPal. Intenta de nuevo en un momento.')
        return redirect('pagos')

    PagoPayPal.objects.create(
        aportacion=ap, usuario=request.user, order_id=order_id,
        monto=ap.monto, moneda=settings.PAYPAL_CURRENCY,
    )
    return redirect(url)


@login_required
def paypal_retorno(request):
    """PayPal regresa aquí tras la aprobación. El servidor captura y verifica el pago."""
    order_id = request.GET.get('token', '')
    pago = (PagoPayPal.objects.select_related('aportacion')
            .filter(order_id=order_id, usuario=request.user).first())
    if pago is None:
        raise Http404

    ap = pago.aportacion
    if pago.estado == 'COMPLETADO':
        # Recarga de la página: no se cobra dos veces.
        return redirect(ap.recibo.get_absolute_url()) if hasattr(ap, 'recibo') else redirect('pagos')
    if pago.estado != 'CREADO':
        messages.error(request, 'Este intento de pago ya no es válido.')
        return redirect('pagos')
    if hasattr(ap, 'recibo'):
        pago.estado, pago.detalle = 'CANCELADO', 'La aportación ya estaba pagada'
        pago.save(update_fields=['estado', 'detalle'])
        messages.info(request, 'Esa aportación ya estaba pagada. No se realizó ningún cargo.')
        return redirect('pagos')

    try:
        captura = paypal.extraer_captura(paypal.capturar_orden(order_id))
        valor = Decimal(captura['value'])
    except (paypal.PayPalError, InvalidOperation) as e:
        log.exception('Falló la captura de PayPal')
        pago.estado, pago.detalle = 'FALLIDO', str(e)[:300]
        pago.save(update_fields=['estado', 'detalle'])
        messages.error(request, 'No se pudo completar el pago con PayPal. No se registró ningún pago.')
        return redirect('pagos')

    # Se verifica que PayPal cobró EXACTAMENTE lo que se esperaba.
    if captura['status'] != 'COMPLETED' or valor != pago.monto or captura['currency'] != pago.moneda:
        pago.estado = 'FALLIDO'
        pago.capture_id = captura['id']
        pago.detalle = f"Captura no válida: {captura['status']} {captura['value']} {captura['currency']}"[:300]
        pago.save(update_fields=['estado', 'capture_id', 'detalle'])
        messages.error(request, 'El pago no pudo confirmarse. Contacta a la administración.')
        return redirect('pagos')

    with transaction.atomic():
        recibo = Recibo.objects.create(
            aportacion=ap, monto=pago.monto, metodo='PayPal',
            observaciones=f"PayPal {captura['id']}",
        )
        ap.pagada = True
        ap.save(update_fields=['pagada'])
        pago.estado, pago.capture_id = 'COMPLETADO', captura['id']
        pago.save(update_fields=['estado', 'capture_id'])

    messages.success(request, f'¡Pago recibido! Tu recibo es el No. {recibo.numero:05d}.')
    return redirect(recibo.get_absolute_url())


@login_required
def paypal_cancelado(request):
    order_id = request.GET.get('token', '')
    PagoPayPal.objects.filter(order_id=order_id, usuario=request.user, estado='CREADO') \
        .update(estado='CANCELADO', detalle='Cancelado por el usuario en PayPal')
    messages.info(request, 'Cancelaste el pago. No se realizó ningún cargo.')
    return redirect('pagos')
