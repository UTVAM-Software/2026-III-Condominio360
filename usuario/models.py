from django.contrib.auth.models import User
from django.db import models


class Perfil(models.Model):
    """Datos del condominio de cada usuario (residente o administrador)."""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    unidad = models.CharField('Departamento / casa', max_length=20, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)

    def __str__(self):
        return f'Perfil de {self.usuario.username}'
