from django.urls import path 

from .views import gastoListView, gastoDetailView, gastoCreateView, gastoUpdateView, gastoDeleteView

urlpatterns = [
    path('gasto/', gastoListView.as_view(), name='gasto-list'),
    path('gasto/<int:pk>/', gastoDetailView.as_view(), name='gasto-detail'),
    path('gasto/create/', gastoCreateView.as_view(), name='gasto-create'),
    path('gasto/<int:pk>/update', gastoUpdateView.as_view(), name='gasto-update'),
    path('gasto/<int:pk>/delete', gastoDeleteView.as_view(), name='gasto-delete'),
]