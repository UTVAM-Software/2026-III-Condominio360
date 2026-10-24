from django.shortcuts import render

# Create your views here.
from .models import gasto

class gastoListView(ListView):
    model = gasto

class gastoDetailView(DetailView):
    model = gasto

class gastoCreateView(CreateView):
    model = gasto
    fields = ['nombre', 'fecha', 'cantidad', 'deuda', 'dias_retraso', 'descripcion']

class gastoUpdateView(UpdateView):
    model = gasto
    fields = ['nombre', 'fecha', 'cantidad', 'deuda', 'dias_retraso', 'descripcion']

class gastoDeleteView(DeleteView):
    model = gasto
    success_url = '/'

# Create your views here.
