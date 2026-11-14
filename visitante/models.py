from django.db import models


class Aviso(models.Model):
    """Aviso público: lo ve cualquier visitante en la página de inicio (solo lectura)."""
    titulo = models.CharField(max_length=150)
    contenido = models.TextField()
    publicado = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return self.titulo
