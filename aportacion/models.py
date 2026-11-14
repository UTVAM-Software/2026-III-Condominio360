from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Aportacion(models.Model):
    """Cuota o aportación que debe pagar un residente."""
    residente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aportaciones')
    concepto = models.CharField(max_length=100, default='Cuota de mantenimiento')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_limite = models.DateField('Fecha límite de pago')
    pagada = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_limite']
        verbose_name = 'aportación'
        verbose_name_plural = 'aportaciones'

    @property
    def dias_retraso(self):
        if self.pagada:
            return 0
        retraso = (timezone.localdate() - self.fecha_limite).days
        return retraso if retraso > 0 else 0

    def get_absolute_url(self):
        return reverse('aportacion:detalle', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.concepto} - {self.residente.username} - ${self.monto}'
