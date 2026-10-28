from django.db import models


class Gasto(models.Model):
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    cantidad = models.DecimalField(max_digits=5, decimal_places=2)
    deuda = models.DecimalField(max_digits=5, decimal_places=2)
    dias_retraso = models.IntegerField(default=0)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nombre} - {self.cantidad} - {self.deuda}"
