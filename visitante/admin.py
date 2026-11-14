from django.contrib import admin

from .models import Aviso


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'publicado', 'creado')
