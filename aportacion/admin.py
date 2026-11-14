from django.contrib import admin

from .models import Aportacion


@admin.register(Aportacion)
class AportacionAdmin(admin.ModelAdmin):
    list_display = ('concepto', 'residente', 'monto', 'fecha_limite', 'pagada')
    list_filter = ('pagada',)
    search_fields = ('concepto', 'residente__username')
