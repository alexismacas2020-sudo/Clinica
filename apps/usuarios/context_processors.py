from django.urls import reverse
from django.conf import settings
from django.db import OperationalError, ProgrammingError
from allauth.socialaccount.models import SocialApp

from .models import Perfil


def usuario_contexto(request):
    google_login_disponible = bool(settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET)
    if not google_login_disponible:
        try:
            google_login_disponible = SocialApp.objects.filter(provider="google", sites__id=settings.SITE_ID).exists()
        except (OperationalError, ProgrammingError):
            google_login_disponible = False
    if not request.user.is_authenticated:
        return {"perfil_actual": None, "url_panel_usuario": None, "google_login_disponible": google_login_disponible}
    perfil, _ = Perfil.objects.get_or_create(
        usuario=request.user,
        defaults={"rol": Perfil.Rol.ADMIN if request.user.is_superuser else Perfil.Rol.PACIENTE},
    )
    rol = Perfil.Rol.ADMIN if request.user.is_superuser else perfil.rol
    destinos = {
        Perfil.Rol.ADMIN: "dashboard:admin",
        Perfil.Rol.RECEPCIONISTA: "dashboard:recepcionista",
        Perfil.Rol.MEDICO: "dashboard:medico",
        Perfil.Rol.PACIENTE: "dashboard:paciente",
    }
    return {
        "perfil_actual": perfil,
        "url_panel_usuario": reverse(destinos[rol]),
        "google_login_disponible": google_login_disponible,
    }
