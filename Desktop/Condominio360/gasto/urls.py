from django.urls import path

from . import views

app_name = 'gasto'

urlpatterns = [
    path('', views.GastoLista.as_view(), name='lista'),
    path('nuevo/', views.GastoCrear.as_view(), name='crear'),
    path('<int:pk>/editar/', views.GastoEditar.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.GastoEliminar.as_view(), name='eliminar'),
]
