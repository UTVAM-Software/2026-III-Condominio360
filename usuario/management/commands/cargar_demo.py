"""Carga datos de demostración: roles, usuarios, aportaciones, recibos y gastos.

Uso:  python manage.py cargar_demo
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from aportacion.models import Aportacion
from gasto.models import Gasto
from recibo.models import Recibo
from usuario.forms import asignar_rol, guardar_perfil
from usuario.permisos import ROL_ADMIN, ROL_RESIDENTE
from visitante.models import Aviso


class Command(BaseCommand):
    help = 'Crea roles, usuarios y datos de ejemplo para la demostración.'

    def handle(self, *args, **options):
        hoy = timezone.localdate()
        for nombre in (ROL_ADMIN, ROL_RESIDENTE):
            Group.objects.get_or_create(name=nombre)

        def usuario(username, password, nombre, apellido, rol, unidad, tel):
            u, creado = User.objects.get_or_create(
                username=username,
                defaults={'first_name': nombre, 'last_name': apellido,
                          'email': f'{username}@condominio360.mx'},
            )
            if creado:
                u.set_password(password)
                u.save()
            guardar_perfil(u, unidad, tel)
            asignar_rol(u, rol)
            return u

        usuario('administrador', 'Admin12345', 'Ana', 'Administradora', ROL_ADMIN, 'Oficina', '5550000000')
        r1 = usuario('residente1', 'Residente12345', 'Luis', 'Pérez', ROL_RESIDENTE, 'A-101', '5551110001')
        r2 = usuario('residente2', 'Residente12345', 'María', 'López', ROL_RESIDENTE, 'B-202', '5551110002')

        if not Aportacion.objects.exists():
            datos = [
                (r1, 'Mantenimiento septiembre', '1200.00', -40, True),
                (r1, 'Mantenimiento octubre', '1200.00', -10, False),
                (r1, 'Mantenimiento noviembre', '1200.00', 20, False),
                (r2, 'Mantenimiento septiembre', '1200.00', -40, True),
                (r2, 'Mantenimiento octubre', '1200.00', -10, True),
                (r2, 'Cuota extraordinaria (portón)', '800.00', 15, False),
            ]
            for residente, concepto, monto, dias, pagada in datos:
                ap = Aportacion.objects.create(
                    residente=residente, concepto=concepto,
                    monto=Decimal(monto), fecha_limite=hoy + timedelta(days=dias),
                )
                if pagada:
                    Recibo.objects.create(
                        aportacion=ap, monto=ap.monto, fecha=ap.fecha_limite,
                        metodo='Transferencia',
                    )
                    ap.pagada = True
                    ap.save(update_fields=['pagada'])

        if not Gasto.objects.exists():
            Gasto.objects.create(nombre='Limpieza de áreas comunes', fecha=hoy - timedelta(days=12),
                                 cantidad=Decimal('900.00'), deuda=Decimal('0'),
                                 descripcion='Servicio mensual de limpieza')
            Gasto.objects.create(nombre='Reparación de bomba de agua', fecha=hoy - timedelta(days=5),
                                 cantidad=Decimal('1500.00'), deuda=Decimal('500.00'),
                                 dias_retraso=5, descripcion='Pendiente de pagar al proveedor')

        if not Aviso.objects.exists():
            Aviso.objects.create(titulo='Mantenimiento de la alberca',
                                 contenido='La alberca estará cerrada el próximo sábado por limpieza y mantenimiento.')
            Aviso.objects.create(titulo='Junta de condóminos',
                                 contenido='Se convoca a la junta mensual el último viernes del mes a las 19:00 h en el salón de usos múltiples.')

        self.stdout.write(self.style.SUCCESS('Datos de demostración listos.'))
        self.stdout.write('  administrador / Admin12345')
        self.stdout.write('  residente1    / Residente12345')
        self.stdout.write('  residente2    / Residente12345')
