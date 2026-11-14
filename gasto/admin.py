from django.contrib import admin

from .models import Gasto


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'cantidad', 'deuda', 'dias_retraso')
