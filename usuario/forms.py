from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User

from .models import Perfil
from .permisos import ROL_ADMIN, ROL_RESIDENTE, es_admin

ROLES = [(ROL_RESIDENTE, 'Residente'), (ROL_ADMIN, 'Administrador')]


def asignar_rol(user, rol):
    """Deja al usuario en un único grupo de rol."""
    for nombre in (ROL_ADMIN, ROL_RESIDENTE):
        grupo, _ = Group.objects.get_or_create(name=nombre)
        user.groups.remove(grupo)
    grupo, _ = Group.objects.get_or_create(name=rol)
    user.groups.add(grupo)


def guardar_perfil(user, unidad, telefono):
    perfil, _ = Perfil.objects.get_or_create(usuario=user)
    perfil.unidad = unidad
    perfil.telefono = telefono
    perfil.save()


class UsuarioCrearForm(UserCreationForm):
    unidad = forms.CharField(label='Departamento / casa', max_length=20, required=False)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    rol = forms.ChoiceField(label='Rol', choices=ROLES, initial=ROL_RESIDENTE)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=True)
        guardar_perfil(user, self.cleaned_data['unidad'], self.cleaned_data['telefono'])
        asignar_rol(user, self.cleaned_data['rol'])
        return user


class UsuarioEditarForm(forms.ModelForm):
    unidad = forms.CharField(label='Departamento / casa', max_length=20, required=False)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    rol = forms.ChoiceField(label='Rol', choices=ROLES)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_active')
        labels = {'is_active': 'Cuenta activa'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        perfil = getattr(self.instance, 'perfil', None)
        if perfil is not None:
            self.fields['unidad'].initial = perfil.unidad
            self.fields['telefono'].initial = perfil.telefono
        self.fields['rol'].initial = ROL_ADMIN if es_admin(self.instance) else ROL_RESIDENTE

    def save(self, commit=True):
        user = super().save(commit=True)
        guardar_perfil(user, self.cleaned_data['unidad'], self.cleaned_data['telefono'])
        if not user.is_superuser:
            asignar_rol(user, self.cleaned_data['rol'])
        return user
