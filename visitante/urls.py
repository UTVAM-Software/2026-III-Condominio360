from django.urls import path

from . import views

app_name = 'visitante'

# Todas estas rutas son del administrador (gestión de avisos públicos).
urlpatterns = [
    path('avisos/', views.AvisoLista.as_view(), name='avisos'),
    path('avisos/nuevo/', views.AvisoCrear.as_view(), name='aviso_crear'),
    path('avisos/<int:pk>/editar/', views.AvisoEditar.as_view(), name='aviso_editar'),
    path('avisos/<int:pk>/eliminar/', views.AvisoEliminar.as_view(), name='aviso_eliminar'),
]
