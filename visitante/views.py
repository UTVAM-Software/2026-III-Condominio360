"""Gestión de los avisos públicos (solo administrador).

El visitante NO tiene vistas propias: solo ve la página pública de inicio
(Finanzas.views.inicio) y no puede enviar ni modificar nada.
"""
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from usuario.permisos import AdminRequeridoMixin, BootstrapFormMixin

from .models import Aviso


class AvisoLista(AdminRequeridoMixin, ListView):
    model = Aviso
    template_name = 'visitante/aviso_list.html'
    context_object_name = 'avisos'


class AvisoCrear(AdminRequeridoMixin, BootstrapFormMixin, CreateView):
    model = Aviso
    fields = ['titulo', 'contenido', 'publicado']
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('visitante:avisos')
    extra_context = {'titulo': 'Nuevo aviso', 'url_cancelar': reverse_lazy('visitante:avisos')}


class AvisoEditar(AdminRequeridoMixin, BootstrapFormMixin, UpdateView):
    model = Aviso
    fields = ['titulo', 'contenido', 'publicado']
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('visitante:avisos')
    extra_context = {'titulo': 'Editar aviso', 'url_cancelar': reverse_lazy('visitante:avisos')}


class AvisoEliminar(AdminRequeridoMixin, DeleteView):
    model = Aviso
    template_name = 'crud/confirmar_eliminar.html'
    success_url = reverse_lazy('visitante:avisos')
    extra_context = {'url_cancelar': reverse_lazy('visitante:avisos')}
