from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from usuario.permisos import AdminRequeridoMixin, BootstrapFormMixin, es_admin

from .forms import AportacionForm
from .models import Aportacion


class SoloPropiasMixin:
    """Control de acceso a nivel de objeto: un residente solo ve lo suyo.

    Al filtrar el queryset, intentar abrir la aportación de otra persona
    (cambiando el número en la URL) devuelve 404 y no revela su existencia.
    """

    def get_queryset(self):
        qs = Aportacion.objects.select_related('residente', 'recibo')
        if es_admin(self.request.user):
            return qs
        return qs.filter(residente=self.request.user)


class AportacionLista(LoginRequiredMixin, SoloPropiasMixin, ListView):
    template_name = 'aportacion/aportacion_list.html'
    context_object_name = 'aportaciones'


class AportacionDetalle(LoginRequiredMixin, SoloPropiasMixin, DetailView):
    template_name = 'aportacion/aportacion_detail.html'
    context_object_name = 'aportacion'


class AportacionCrear(AdminRequeridoMixin, BootstrapFormMixin, CreateView):
    model = Aportacion
    form_class = AportacionForm
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('aportacion:lista')
    extra_context = {'titulo': 'Nueva aportación', 'url_cancelar': reverse_lazy('aportacion:lista')}


class AportacionEditar(AdminRequeridoMixin, BootstrapFormMixin, UpdateView):
    model = Aportacion
    form_class = AportacionForm
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('aportacion:lista')
    extra_context = {'titulo': 'Editar aportación', 'url_cancelar': reverse_lazy('aportacion:lista')}


class AportacionEliminar(AdminRequeridoMixin, DeleteView):
    model = Aportacion
    template_name = 'crud/confirmar_eliminar.html'
    success_url = reverse_lazy('aportacion:lista')
    extra_context = {'url_cancelar': reverse_lazy('aportacion:lista')}
