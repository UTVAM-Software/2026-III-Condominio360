from django.db import models

# Create your models here.
class Concepto(models.Model):
    nombre = models.CharField(max_length=100)
    lugar = models.CharField(max_length=100)
    fecha = models.DateField()
    cuenta = models.DecimalField(5,2)
    aportacion = models.DecimalField(5,2)
    numero_recibo = models.DecimalField(5,2)
    