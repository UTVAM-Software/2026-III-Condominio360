from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.urls import reverse
from django.utils import timezone


class Recibo(models.Model):
    """Comprobante de pago de una aportación."""
    METODOS = [
        ('Efectivo', 'Efectivo'),
        ('Transferencia', 'Transferencia'),
        ('Tarjeta', 'Tarjeta'),
        ('PayPal', 'PayPal'),
    ]

    aportacion = models.OneToOneField('aportacion.Aportacion', on_delete=models.CASCADE,
                                      related_name='recibo')
    numero = models.PositiveIntegerField('Número de recibo', unique=True, editable=False)
    fecha = models.DateField(default=timezone.localdate)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField('Método de pago', max_length=20, choices=METODOS, default='Efectivo')
    observaciones = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-numero']

    def save(self, *args, **kwargs):
        if not self.numero:
            ultimo = Recibo.objects.aggregate(m=Max('numero'))['m'] or 0
            self.numero = ultimo + 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('recibo:detalle', kwargs={'pk': self.pk})

    def __str__(self):
        return f'Recibo {self.numero:05d}'


class PagoPayPal(models.Model):
    """Intento de pago en línea. Liga la orden de PayPal con la aportación y el usuario."""
    ESTADOS = [
        ('CREADO', 'Creado'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
        ('FALLIDO', 'Fallido'),
    ]

    aportacion = models.ForeignKey('aportacion.Aportacion', on_delete=models.CASCADE,
                                   related_name='pagos_paypal')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pagos_paypal')
    order_id = models.CharField(max_length=64, unique=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, default='MXN')
    estado = models.CharField(max_length=12, choices=ESTADOS, default='CREADO')
    capture_id = models.CharField(max_length=64, blank=True)
    detalle = models.CharField(max_length=300, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'pago PayPal'
        verbose_name_plural = 'pagos PayPal'

    def __str__(self):
        return f'{self.order_id} · {self.estado}'
