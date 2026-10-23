from django.shortcuts import render

# Create your views here.
from .models import usuario

class usuarioListView(ListView):
    model = usuario

class usuarioDetailView(DetailView):
    model = usuario

class usuarioCreateView(CreateView):
    model = usuario
    fields = ['nombre','lugar' ,'fecha', 'password', 'correo_electronico', 'pago_mensual', 'pago_total', 'pago_instalacion']

class usuarioUpdateView(UpdateView):
    model = usuario
    fields = ['nombre','lugar' ,'fecha', 'password', 'correo_electronico', 'pago_mensual', 'pago_total', 'pago_instalacion']

class usuarioDeleteView(DeleteView):
    model = usuario
    success_url = '/'


   
      
