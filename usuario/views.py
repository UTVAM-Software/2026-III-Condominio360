from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import UsuarioCrearForm, UsuarioEditarForm
from .permisos import AdminRequeridoMixin, BootstrapFormMixin


class UsuarioLista(AdminRequeridoMixin, ListView):
    model = User
    template_name = 'usuario/usuario_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return User.objects.select_related('perfil').prefetch_related('groups').order_by('username')


class UsuarioCrear(AdminRequeridoMixin, BootstrapFormMixin, CreateView):
    model = User
    form_class = UsuarioCrearForm
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('usuario:lista')
    extra_context = {'titulo': 'Nuevo usuario', 'url_cancelar': reverse_lazy('usuario:lista')}


class UsuarioEditar(AdminRequeridoMixin, BootstrapFormMixin, UpdateView):
    model = User
    form_class = UsuarioEditarForm
    template_name = 'crud/formulario.html'
    success_url = reverse_lazy('usuario:lista')
    extra_context = {'titulo': 'Editar usuario', 'url_cancelar': reverse_lazy('usuario:lista')}
