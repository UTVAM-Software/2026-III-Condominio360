from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from aportacion.models import Aportacion
from usuario.permisos import AdminRequeridoMixin, BootstrapFormMixin, es_admin

from .models import Recibo


class SoloPropiosMixin:
    """Un residente solo ve los recibos de sus propias aportaciones."""

    def get_queryset(self):
        qs = Recibo.objects.select_related('aportacion', 'aportacion__residente')
        if es_admin(self.request.user):
            return qs
        return qs.filter(aportacion__residente=self.request.user)


class ReciboLista(LoginRequiredMixin, SoloPropiosMixin, ListView):
    template_name = 'recibo/recibo_list.html'
    context_object_name = 'recibos'


class ReciboDetalle(LoginRequiredMixin, SoloPropiosMixin, DetailView):
    template_name = 'recibo/recibo_detail.html'
    context_object_name = 'recibo'


class ReciboCrear(AdminRequeridoMixin, BootstrapFormMixin, CreateView):
    """Registra el pago de una aportación y genera su recibo."""
    model = Recibo
    fields = ['fecha', 'monto', 'metodo', 'observaciones']
    template_name = 'crud/formulario.html'

    def _aportacion(self):
        if not hasattr(self, '_ap'):
            self._ap = get_object_or_404(Aportacion, pk=self.kwargs['aportacion_id'])
        return self._ap

    def _ya_pagada(self):
        ap = self._aportacion()
        if hasattr(ap, 'recibo'):
            return redirect(ap.recibo.get_absolute_url())
        return None

    def get(self, request, *args, **kwargs):
        return self._ya_pagada() or super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._ya_pagada() or super().post(request, *args, **kwargs)

    def get_initial(self):
        return {'monto': self._aportacion().monto}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ap = self._aportacion()
        ctx['titulo'] = f'Registrar pago: {ap.concepto} ({ap.residente.get_full_name() or ap.residente.username})'
        ctx['url_cancelar'] = reverse_lazy('aportacion:lista')
        return ctx

    def form_valid(self, form):
        ap = self._aportacion()
        with transaction.atomic():
            form.instance.aportacion = ap
            respuesta = super().form_valid(form)
            ap.pagada = True
            ap.save(update_fields=['pagada'])
        return respuesta


class ReciboEliminar(AdminRequeridoMixin, DeleteView):
    model = Recibo
    template_name = 'crud/confirmar_eliminar.html'
    success_url = reverse_lazy('recibo:lista')
    extra_context = {'url_cancelar': reverse_lazy('recibo:lista')}

    def form_valid(self, form):
        ap = self.object.aportacion
        respuesta = super().form_valid(form)
        ap.pagada = False
        ap.save(update_fields=['pagada'])
        return respuesta
