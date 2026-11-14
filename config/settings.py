"""Configuración de Condominio360."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-wh(!tyo0ue4pwr10s)_w--a6b35fu@q2pr6-7@-lo44jmy2mou'

# Solo para desarrollo/demo. En producción: DEBUG = False y ALLOWED_HOSTS definido.
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps del condominio
    'usuario',
    'aportacion',
    'recibo',
    'visitante',
    'gasto',
    'Finanzas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'usuario.middleware.SoloLecturaMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'usuario.context.roles',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Inicio y cierre de sesión
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'inicio'
LOGOUT_REDIRECT_URL = 'login'

# Endurecimiento básico de sesión/cookies
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 8  # 8 horas

# Datos que verá el residente en "Pagos" para realizar su depósito o transferencia.
# CAMBIA estos valores por los reales de tu condominio.
DATOS_PAGO = {
    'banco': 'Banco de ejemplo',
    'titular': 'Condominio360 A.C.',
    'clabe': '000000000000000000',
    'instrucciones': 'Realiza tu transferencia o depósito y entrega el comprobante a la administración. '
                     'Tu recibo se generará cuando el administrador registre el pago.',
}

# --- PayPal (las credenciales se leen del entorno; NUNCA las escribas en el código) ---
# En PowerShell, antes de runserver:
#   $env:PAYPAL_CLIENT_ID="tu_client_id_sandbox"
#   $env:PAYPAL_CLIENT_SECRET="tu_secret_sandbox"
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')      # 'sandbox' (pruebas) o 'live'
PAYPAL_CURRENCY = os.environ.get('PAYPAL_CURRENCY', 'MXN')  # si PayPal la rechaza, prueba 'USD'

# Información pública que ve el visitante en la página de inicio (cámbiala por la real).
INFO_CONDOMINIO = {
    'nombre': 'Condominio360',
    'descripcion': 'Residencial con áreas verdes, alberca, salón de usos múltiples y vigilancia las 24 horas.',
    'direccion': 'Calle Ejemplo 123, Col. Centro',
    'horario': 'Administración: lunes a viernes de 9:00 a 17:00 h',
    'telefono': '55 0000 0000',
    'correo': 'administracion@condominio360.mx',
    'areas': [
        'Alberca: todos los días de 8:00 a 20:00 h',
        'Salón de usos múltiples: previa reservación con la administración',
        'Gimnasio: de 6:00 a 22:00 h',
        'Áreas verdes y juegos infantiles: de 7:00 a 21:00 h',
    ],
    'reglamento': [
        'Las visitas deben registrarse con la administración o en la caseta.',
        'Horario de silencio: 22:00 a 7:00 h.',
        'Los proveedores y personal de servicio deben presentar identificación.',
        'El estacionamiento de visitas es limitado y por tiempo máximo de 4 horas.',
    ],
}
