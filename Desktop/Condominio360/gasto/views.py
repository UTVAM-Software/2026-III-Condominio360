from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Gasto


class GastoLista(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Gasto
    permission_required = 'gasto.view_gasto'
    template_name = 'crud/lista.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx.update({
            'titulo': 'Gastos',
            'url_crear': reverse_lazy('gasto:crear'),
            'url_editar': 'gasto:editar',
            'url_eliminar': 'gasto:eliminar',
            'puede_crear': u.has_perm('gasto.add_gasto'),
            'puede_editar': u.has_perm('gasto.change_gasto'),
            'puede_eliminar': u.has_perm('gasto.delete_gasto'),
        })
        return ctx


class GastoCrear(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Gasto
    fields = '__all__'
    permission_required = 'gasto.add_gasto'
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('gasto:lista')
    extra_context = {'titulo': 'Nuevo gasto', 'url_cancelar': reverse_lazy('gasto:lista')}


class GastoEditar(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Gasto
    fields = '__all__'
    permission_required = 'gasto.change_gasto'
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('gasto:lista')
    extra_context = {'titulo': 'Editar gasto', 'url_cancelar': reverse_lazy('gasto:lista')}


class GastoEliminar(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Gasto
    permission_required = 'gasto.delete_gasto'
    template_name = 'crud/confirmar_eliminar.html'
    success_url = reverse_lazy('gasto:lista')
    extra_context = {'url_cancelar': reverse_lazy('gasto:lista')}
