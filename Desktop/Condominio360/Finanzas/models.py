from django.db import models

class Concepto(models.Model):
    nombre = models.CharField(max_length=100)
    lugar = models.CharField(max_length=100)
    fecha = models.DateField()
    cantidad = models.DecimalField(5,2)
    deuda = models.DecimalField(5,2)
    numero_recibo = models.DecimalField(5,2)
    cuenta = models.DecimalField(5,2)

    def __str__(self):
        return f"{self.nombre}  -  {self.cantidad} - {self.deuda} - {self.numero_recibo} - {self.cuenta}"