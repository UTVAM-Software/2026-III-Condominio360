from django.contrib import admin

from .models import Recibo


@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ('numero', 'aportacion', 'monto', 'fecha', 'metodo')


from .models import PagoPayPal  # noqa: E402


@admin.register(PagoPayPal)
class PagoPayPalAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'usuario', 'aportacion', 'monto', 'moneda', 'estado', 'creado')
    list_filter = ('estado',)
    readonly_fields = ('creado',)
