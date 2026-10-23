from django.db import models

class Concepto(models.Model):
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    cantidad = models.DecimalField(5,2)
    deuda = models.DecimalField(5,2)
    dias_retraso = models.CharField(5,2)
    descripcion = models.CharField(max_length=200)
        
    