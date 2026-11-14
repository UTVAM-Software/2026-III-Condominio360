import csv

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from gasto.models import Gasto
from recibo import paypal
from usuario.permisos import ROL_ADMIN, es_admin
from visitante.models import Aviso

from .servicios import (MESES, aportaciones_de, datos_grafica, rango_mes,
                        recibos_de, resumen_mes, suma)


def inicio(request):
    """Visitante (sin sesión): página pública. Con sesión: panel según el rol."""
    if not request.user.is_authenticated:
        return render(request, 'Finanzas/publico.html', {
            'avisos': Aviso.objects.filter(publicado=True)[:5],
            'info': settings.INFO_CONDOMINIO,
        })
    user = request.user
    admin = es_admin(user)
    pendientes = aportaciones_de(user).filter(pagada=False)
    vencidas = pendientes.filter(fecha_limite__lt=timezone.localdate()).order_by('fecha_limite')
    cobrado = suma(recibos_de(user), 'monto')

    contexto = {
        'total_cobrado': cobrado,
        'total_por_cobrar': suma(pendientes, 'monto'),
        'num_pendientes': pendientes.count(),
        'vencidas': vencidas[:10],
        'num_vencidas': vencidas.count(),
        'grafica': datos_grafica(user),
    }
    if admin:
        gastos = suma(Gasto.objects.all(), 'cantidad')
        contexto.update({
            'total_gastos': gastos,
            'balance': cobrado - gastos,
            'num_usuarios': User.objects.filter(is_active=True).count(),
        })
    return render(request, 'Finanzas/inicio.html', contexto)


@login_required
def pagos(request):
    """Módulo de pagos. Administrador: cobranza. Residente: lo que debe y cómo pagar (solo lectura)."""
    user = request.user
    admin = es_admin(user)
    hoy = timezone.localdate()
    pendientes = aportaciones_de(user).filter(pagada=False).order_by('fecha_limite')

    perfil = getattr(user, 'perfil', None)
    contexto = {
        'pendientes': pendientes,
        'total_adeudo': suma(pendientes, 'monto'),
        'total_vencido': suma(pendientes.filter(fecha_limite__lt=hoy), 'monto'),
        'historial': recibos_de(user)[:15],
        'datos_pago': settings.DATOS_PAGO,
        'referencia': (perfil.unidad if perfil and perfil.unidad else user.username),
        'hoy': hoy,
        'paypal_activo': paypal.configurado(),
        'moneda': settings.PAYPAL_CURRENCY,
    }
    if admin:
        residentes = (
            User.objects.filter(is_active=True)
            .exclude(is_superuser=True).exclude(groups__name=ROL_ADMIN)
            .annotate(
                adeudo=Sum('aportaciones__monto', filter=Q(aportaciones__pagada=False)),
                pagado=Sum('aportaciones__recibo__monto'),
            )
            .select_related('perfil').order_by('username')
        )
        contexto['residentes'] = residentes
        ini, fin = rango_mes(hoy.year, hoy.month)
        contexto['cobrado_mes'] = suma(
            recibos_de(user).filter(fecha__gte=ini, fecha__lt=fin), 'monto')
    return render(request, 'Finanzas/pagos.html', contexto)


@login_required
def reporte_mensual(request):
    user = request.user
    admin = es_admin(user)
    hoy = timezone.localdate()
    try:
        anio = int(request.GET.get('anio', hoy.year))
        mes = int(request.GET.get('mes', hoy.month))
        if not (1 <= mes <= 12 and 2000 <= anio <= 2100):
            raise ValueError
    except ValueError:
        anio, mes = hoy.year, hoy.month

    ini, fin = rango_mes(anio, mes)
    recibos = recibos_de(user).filter(fecha__gte=ini, fecha__lt=fin).order_by('fecha', 'numero')
    aportaciones = aportaciones_de(user).filter(
        fecha_limite__gte=ini, fecha_limite__lt=fin).order_by('fecha_limite')
    gastos = Gasto.objects.filter(fecha__gte=ini, fecha__lt=fin).order_by('fecha') if admin else []
    resumen = resumen_mes(user, anio, mes)

    if request.GET.get('formato') == 'csv':
        resp = HttpResponse(content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = f'attachment; filename="reporte_{anio}_{mes:02d}.csv"'
        resp.write('\ufeff')  # para que Excel respete los acentos
        w = csv.writer(resp)
        w.writerow([f'Reporte {MESES[mes - 1]} {anio}'])
        w.writerow([])
        w.writerow(['INGRESOS (recibos)'])
        w.writerow(['No.', 'Residente', 'Concepto', 'Fecha', 'Monto', 'Método'])
        for r in recibos:
            w.writerow([r.numero, r.aportacion.residente.get_full_name() or r.aportacion.residente.username,
                        r.aportacion.concepto, r.fecha.strftime('%d/%m/%Y'), r.monto, r.metodo])
        if admin:
            w.writerow([])
            w.writerow(['GASTOS'])
            w.writerow(['Nombre', 'Fecha', 'Cantidad', 'Deuda', 'Descripción'])
            for g in gastos:
                w.writerow([g.nombre, g.fecha.strftime('%d/%m/%Y'), g.cantidad, g.deuda, g.descripcion])
            w.writerow([])
            w.writerow(['Total cobrado', resumen['cobrado']])
            w.writerow(['Total gastos', resumen['gastos']])
            w.writerow(['Balance', resumen['balance']])
        return resp

    return render(request, 'Finanzas/reporte.html', {
        'anio': anio, 'mes': mes, 'mes_nombre': MESES[mes - 1],
        'meses': list(enumerate(MESES, start=1)),
        'anios': range(hoy.year - 3, hoy.year + 1),
        'resumen': resumen, 'recibos': recibos, 'aportaciones': aportaciones,
        'gastos': gastos, 'grafica': datos_grafica(user),
    })
