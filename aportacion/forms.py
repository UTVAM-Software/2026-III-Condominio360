from django import forms
from django.contrib.auth.models import User

from .models import Aportacion


class ResidenteChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, u):
        nombre = u.get_full_name() or u.username
        perfil = getattr(u, 'perfil', None)
        unidad = perfil.unidad if perfil else ''
        return f'{nombre} ({unidad})' if unidad else nombre


class AportacionForm(forms.ModelForm):
    residente = ResidenteChoiceField(
        queryset=User.objects.filter(is_active=True).select_related('perfil').order_by('username')
    )

    class Meta:
        model = Aportacion
        fields = ['residente', 'concepto', 'monto', 'fecha_limite']
