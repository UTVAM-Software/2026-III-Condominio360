from django.urls import path

from . import paypal_views, views

app_name = 'recibo'

urlpatterns = [
    path('', views.ReciboLista.as_view(), name='lista'),
    path('pagar/<int:aportacion_id>/', views.ReciboCrear.as_view(), name='crear'),
    path('<int:pk>/', views.ReciboDetalle.as_view(), name='detalle'),
    path('<int:pk>/eliminar/', views.ReciboEliminar.as_view(), name='eliminar'),
    # Pago en línea con PayPal
    path('paypal/iniciar/<int:aportacion_id>/', paypal_views.paypal_iniciar, name='paypal_iniciar'),
    path('paypal/retorno/', paypal_views.paypal_retorno, name='paypal_retorno'),
    path('paypal/cancelado/', paypal_views.paypal_cancelado, name='paypal_cancelado'),
]
