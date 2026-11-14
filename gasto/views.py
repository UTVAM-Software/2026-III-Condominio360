from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from usuario.permisos import AdminRequeridoMixin, BootstrapFormMixin

from .models import Gasto


class GastoLista(AdminRequeridoMixin, ListView):
    model = Gasto
    template_name = 'gasto/gasto_list.html'
    context_object_name = 'gastos'


class GastoCrear(AdminRequeridoMixin, BootstrapFormMixin, CreateView):
    model = Gasto
    fields = '__all__'
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('gasto:lista')
    extra_context = {'titulo': 'Nuevo gasto', 'url_cancelar': reverse_lazy('gasto:lista')}


class GastoEditar(AdminRequeridoMixin, BootstrapFormMixin, UpdateView):
    model = Gasto
    fields = '__all__'
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('gasto:lista')
    extra_context = {'titulo': 'Editar gasto', 'url_cancelar': reverse_lazy('gasto:lista')}


class GastoEliminar(AdminRequeridoMixin, DeleteView):
    model = Gasto
    template_name = 'crud/confirmar_eliminar.html'
    success_url = reverse_lazy('gasto:lista')
    extra_context = {'url_cancelar': reverse_lazy('gasto:lista')}
