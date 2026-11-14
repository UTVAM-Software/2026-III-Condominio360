from django.core.exceptions import PermissionDenied
from django.urls import reverse

METODOS_SEGUROS = ('GET', 'HEAD', 'OPTIONS', 'TRACE')

# Lo único que puede enviar alguien SIN sesión (visitante): iniciar sesión.
RUTAS_ANONIMAS = ('/login/', '/logout/', '/admin/login/')

# Excepción del residente: iniciar el pago de SU propia aportación (PayPal).
PREFIJOS_PERMITIDOS = ('/recibos/paypal/iniciar/',)


class SoloLecturaMiddleware:
    """Solo lectura para visitantes y residentes.

    - Visitante (sin sesión): cualquier POST/PUT/PATCH/DELETE se rechaza con 403,
      salvo el inicio de sesión.
    - Residente: lo mismo, salvo iniciar/cerrar sesión y su pago en línea.
    - Administrador: sin restricción.
    Funciona aunque alguien intente saltarse la interfaz.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from .permisos import es_admin

        if request.method not in METODOS_SEGUROS:
            user = request.user
            if not user.is_authenticated:
                if request.path not in RUTAS_ANONIMAS:
                    raise PermissionDenied
            elif (
                request.path not in (reverse('login'), reverse('logout'))
                and not request.path.startswith(PREFIJOS_PERMITIDOS)
                and not es_admin(user)
            ):
                raise PermissionDenied
        return self.get_response(request)
