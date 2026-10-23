from django.urls import path 

from .views import reciboListView, reciboDetailView, reciboCreateView, reciboUpdateView, reciboDeleteView

urlpatterns = [
    path('recibo/', reciboListView.as_view(), name='recibo-list'),
    path('recibo/<int:pk>/', reciboDetailView.as_view(), name='recibo-detail'),
    path('recibo/create/', reciboCreateView.as_view(), name='recibo-create'),
    path('recibo/<int:pk>/update', reciboUpdateView.as_view(), name='recibo-update'),
    path('recibo/<int:pk>/delete', reciboDeleteView.as_view(), name='recibo-delete'),
]