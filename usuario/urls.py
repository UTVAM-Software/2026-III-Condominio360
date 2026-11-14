from django.urls import path

from . import views

app_name = 'usuario'

urlpatterns = [
    path('', views.UsuarioLista.as_view(), name='lista'),
    path('nuevo/', views.UsuarioCrear.as_view(), name='crear'),
    path('<int:pk>/editar/', views.UsuarioEditar.as_view(), name='editar'),
]
