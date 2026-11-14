from django.urls import path

from . import views

app_name = 'aportacion'

urlpatterns = [
    path('', views.AportacionLista.as_view(), name='lista'),
    path('nueva/', views.AportacionCrear.as_view(), name='crear'),
    path('<int:pk>/', views.AportacionDetalle.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.AportacionEditar.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.AportacionEliminar.as_view(), name='eliminar'),
]
