from .permisos import es_admin


def roles(request):
    """Hace disponible `es_admin` en todas las plantillas."""
    return {'es_admin': es_admin(request.user)}
