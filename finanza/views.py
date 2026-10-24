from django.shortcuts import render

# Create your views here.
from .models import recibo

class reciboListView(ListView):
    model = recibo

class reciboDetailView(DetailView):
    model = recibo

class reciboCreateView(CreateView):
    model = recibo
    fields = ['nombre', 'lugar', 'fecha', 'cantidad', 'deuda', 'numero_recibo', 'cuenta']

class reciboUpdateView(UpdateView):
    model = recibo
    fields = ['nombre', 'lugar', 'fecha', 'cantidad', 'deuda', 'numero_recibo']

class reciboDeleteView(DeleteView):
    model = recibo
    success_url = '/'