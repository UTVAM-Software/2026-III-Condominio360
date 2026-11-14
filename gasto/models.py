from django.db import models


class Gasto(models.Model):
    """Gasto del condominio (solo lo administra el Administrador)."""
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    deuda = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dias_retraso = models.IntegerField(default=0)
    descripcion = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.nombre} - ${self.cantidad}'
