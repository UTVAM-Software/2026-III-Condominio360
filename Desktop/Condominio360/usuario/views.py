from django.shortcuts import render

# Create your views here.

from .models import finanza

class finazaListView(ListView):
    model = finanza

class finazaDetailView(DetailView):
    model = finanza

class finazaCreateView(CreateView):
    model = finanza
    fields = ['nombre', 'lugar', 'fecha', 'cantidad', 'deuda', 'numero_recibo', 'cuenta']

class finazaUpdateView(UpdateView):
    model = finanza
    fields = ['nombre', 'lugar', 'fecha', 'cantidad', 'deuda', 'numero_recibo', 'cuenta']

class finazaDeleteView(DeleteView):
    model = finanza
    success_url = '/'