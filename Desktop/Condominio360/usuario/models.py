from django.db import models

# Create your models here.
class Concepto(models.Model):
    nombre = models.CharField(max_length=100)
    lugar = models.CharField(max_length=100)
    fecha = models.DateField()
    password = models.CharField(max_length=100)
    correo_electronico = models.CharField(max_length=100)
    Pago_mensual = models.DecimalField(5,2)
    Pago_Total= models.DecimalField(5,2)
    Pago_Instalacion= models.DecimalField(5,2)