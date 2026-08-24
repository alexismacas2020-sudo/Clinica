from django.db import OperationalError, ProgrammingError

from .models import ConfiguracionContacto, ConfiguracionEmergencia


def emergencia_contexto(request):
    try:
        configuracion = ConfiguracionEmergencia.objects.filter(activo=True).order_by("pk").first()
    except (OperationalError, ProgrammingError):
        configuracion = None
    return {"configuracion_emergencia": configuracion}


def contacto_contexto(request):
    try:
        configuracion = ConfiguracionContacto.objects.filter(activo=True).order_by("pk").first()
    except (OperationalError, ProgrammingError):
        configuracion = None
    return {"configuracion_contacto": configuracion}
