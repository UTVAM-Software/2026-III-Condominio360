"""
URL configuration for ciberseguridad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('finanzas', include('finanza.urls')),
    path('recibo', include('recibo.urls')),
    path('gastos', include('gastos.urls')),
    path('correo', include('correo.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # login, logout, etc.
    path('', login_required(TemplateView.as_view(template_name='inicio.html')), name='inicio'),
    path('seguridad/', include('usuario.urls_seguridad')),
    path('gasto/', include('gasto.urls')),
    # una línea por cada app: finanza, recibo, correo, etc.
]



