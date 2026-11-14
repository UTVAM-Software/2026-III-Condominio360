"""Cálculos compartidos por el panel, los pagos y los reportes."""
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from aportacion.models import Aportacion
from gasto.models import Gasto
from recibo.models import Recibo
from usuario.permisos import es_admin

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
         'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def aportaciones_de(user):
    """Administrador: todas. Residente: solo las suyas."""
    qs = Aportacion.objects.select_related('residente')
    return qs if es_admin(user) else qs.filter(residente=user)


def recibos_de(user):
    qs = Recibo.objects.select_related('aportacion', 'aportacion__residente')
    return qs if es_admin(user) else qs.filter(aportacion__residente=user)


def suma(qs, campo):
    return qs.aggregate(t=Sum(campo))['t'] or Decimal('0')


def rango_mes(anio, mes):
    inicio = date(anio, mes, 1)
    fin = date(anio + 1, 1, 1) if mes == 12 else date(anio, mes + 1, 1)
    return inicio, fin


def resumen_mes(user, anio, mes):
    ini, fin = rango_mes(anio, mes)
    admin = es_admin(user)
    cobrado = suma(recibos_de(user).filter(fecha__gte=ini, fecha__lt=fin), 'monto')
    esperadas = aportaciones_de(user).filter(fecha_limite__gte=ini, fecha_limite__lt=fin)
    esperado = suma(esperadas, 'monto')
    pendiente = suma(esperadas.filter(pagada=False), 'monto')
    gastos = balance = None
    if admin:
        gastos = suma(Gasto.objects.filter(fecha__gte=ini, fecha__lt=fin), 'cantidad')
        balance = cobrado - gastos
    return {'cobrado': cobrado, 'esperado': esperado, 'pendiente': pendiente,
            'gastos': gastos, 'balance': balance}


def ultimos_meses(n=6):
    hoy = timezone.localdate()
    anio, mes = hoy.year, hoy.month
    lista = []
    for _ in range(n):
        lista.append((anio, mes))
        mes -= 1
        if mes == 0:
            mes, anio = 12, anio - 1
    return list(reversed(lista))


def datos_grafica(user):
    """Series para Chart.js (listas de números simples)."""
    etiquetas, cobrado, pendiente, gastos, balance = [], [], [], [], []
    for anio, mes in ultimos_meses():
        r = resumen_mes(user, anio, mes)
        etiquetas.append(f'{MESES[mes - 1][:3]} {anio}')
        cobrado.append(float(r['cobrado']))
        pendiente.append(float(r['pendiente']))
        if r['gastos'] is not None:
            gastos.append(float(r['gastos']))
            balance.append(float(r['balance']))

    hoy = timezone.localdate()
    ap = aportaciones_de(user)
    estado = [
        ap.filter(pagada=True).count(),
        ap.filter(pagada=False, fecha_limite__gte=hoy).count(),
        ap.filter(pagada=False, fecha_limite__lt=hoy).count(),
    ]
    return {'es_admin': es_admin(user), 'etiquetas': etiquetas, 'cobrado': cobrado,
            'pendiente': pendiente, 'gastos': gastos, 'balance': balance, 'estado': estado}
