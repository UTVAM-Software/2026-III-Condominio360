from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('pagos/', views.pagos, name='pagos'),
    path('reportes/', views.reporte_mensual, name='reporte'),
]
