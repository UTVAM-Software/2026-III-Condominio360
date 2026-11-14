"""Control de acceso del proyecto.

Roles (grupos de Django):
  - Administrador: ve y gestiona todo.
  - Residente: solo ve SUS aportaciones y SUS recibos.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import CheckboxInput, DateInput, Select

ROL_ADMIN = 'Administrador'
ROL_RESIDENTE = 'Residente'


def es_admin(user):
    if not getattr(user, 'is_authenticated', False):
        return False
    return user.is_superuser or user.groups.filter(name=ROL_ADMIN).exists()


class AdminRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Sin sesión -> login. Con sesión pero sin rol de administrador -> 403."""

    def test_func(self):
        return es_admin(self.request.user)


class BootstrapFormMixin:
    """Aplica estilos de Bootstrap a los formularios de las vistas genéricas."""

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for campo in form.fields.values():
            w = campo.widget
            if isinstance(w, CheckboxInput):
                css = 'form-check-input'
            elif isinstance(w, Select):
                css = 'form-select'
            else:
                css = 'form-control'
            w.attrs['class'] = (w.attrs.get('class', '') + ' ' + css).strip()
            if isinstance(w, DateInput):
                w.input_type = 'date'
                w.format = '%Y-%m-%d'
        return form
