from django.urls import path 

from .views import usuarioListView, usuarioDetailView, usuarioCreateView, usuarioUpdateView, usuarioDeleteView

urlpatterns = [
    path('usuario/', usuarioListView.as_view(), name='usuario-list'),
    path('usuario/<int:pk>/', usuarioDetailView.as_view(), name='usuario-detail'),
    path('usuario/create/', usuarioCreateView.as_view(), name='usuario-create'),
    path('usuario/<int:pk>/update', usuarioUpdateView.as_view(), name='usuario-update'),
    path('usuario/<int:pk>/delete', usuarioDeleteView.as_view(), name='usuario-delete'),
]