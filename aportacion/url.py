from django.urls import path 

from .views import finazaListView, finazaDetailView, finazaCreateView, finazaUpdateView, finazaDeleteView

urlpatterns = [
    path('finanza/', finazaListView.as_view(), name='finanza-list'),
    path('finanza/<int:pk>/', finazaDetailView.as_view(), name='finanza-detail'),
    path('finanza/create/', finazaCreateView.as_view(), name='finanza-create'),
    path('finanza/<int:pk>/update', finazaUpdateView.as_view(), name='finanza-update'),
    path('finanza/<int:pk>/delete', finazaDeleteView.as_view(), name='finanza-delete'),
]