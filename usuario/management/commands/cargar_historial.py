"""Genera 5 meses de historial (aportaciones, recibos y gastos) para que las
gráficas y reportes mensuales tengan datos.  Es seguro correrlo varias veces.

Uso:  python manage.py cargar_historial
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from aportacion.models import Aportacion
from Finanzas.servicios import MESES, ultimos_meses
from gasto.models import Gasto
from recibo.models import Recibo


class Command(BaseCommand):
    help = 'Crea historial de los últimos meses para la demostración.'

    def handle(self, *args, **options):
        residentes = list(User.objects.filter(username__in=['residente1', 'residente2']))
        if not residentes:
            self.stdout.write(self.style.ERROR('Primero corre: python manage.py cargar_demo'))
            return

        hoy = timezone.localdate()
        # 5 meses anteriores al actual
        meses = [m for m in ultimos_meses(6) if m != (hoy.year, hoy.month)]
        creadas = 0
        for i, (anio, mes) in enumerate(meses):
            concepto = f'Mantenimiento {MESES[mes - 1].lower()} {anio}'
            for r in residentes:
                if Aportacion.objects.filter(residente=r, concepto=concepto).exists():
                    continue
                ap = Aportacion.objects.create(
                    residente=r, concepto=concepto, monto=Decimal('1200.00'),
                    fecha_limite=date(anio, mes, 10))
                creadas += 1
                # el residente2 se atrasa en el mes más reciente del historial
                if not (r.username == 'residente2' and i == len(meses) - 1):
                    Recibo.objects.create(
                        aportacion=ap, monto=ap.monto, fecha=date(anio, mes, 8 + (i % 3)),
                        metodo='Transferencia' if i % 2 else 'Efectivo')
                    ap.pagada = True
                    ap.save(update_fields=['pagada'])
            nombre = f'Gastos generales {MESES[mes - 1].lower()} {anio}'
            if not Gasto.objects.filter(nombre=nombre).exists():
                Gasto.objects.create(
                    nombre=nombre, fecha=date(anio, mes, 15),
                    cantidad=Decimal(1400 + (i * 230) % 900), deuda=Decimal('0'),
                    descripcion='Limpieza, luz de áreas comunes y mantenimiento')
        self.stdout.write(self.style.SUCCESS(f'Historial listo ({creadas} aportaciones nuevas).'))
