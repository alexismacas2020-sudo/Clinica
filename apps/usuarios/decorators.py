from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Perfil


def usuario_con_perfil_activo(view_func):
    @login_required
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        perfil, _ = Perfil.objects.get_or_create(usuario=request.user, defaults={"rol": Perfil.Rol.ADMIN if request.user.is_superuser else Perfil.Rol.PACIENTE})
        if not perfil.activo:
            logout(request)
            messages.error(request, "Tu cuenta no está habilitada.")
            return redirect("usuarios:login")
        return view_func(request, *args, **kwargs)
    return wrapped


def roles_requeridos(*roles):
    def decorator(view_func):
        @usuario_con_perfil_activo
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.user.is_superuser or request.user.perfil.rol in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("No tienes permiso para acceder a esta sección.")
        return wrapped
    return decorator


solo_administrador = roles_requeridos(Perfil.Rol.ADMIN)
solo_recepcionista = roles_requeridos(Perfil.Rol.RECEPCIONISTA)
solo_medico = roles_requeridos(Perfil.Rol.MEDICO)
solo_paciente = roles_requeridos(Perfil.Rol.PACIENTE)
administrador_o_recepcionista = roles_requeridos(Perfil.Rol.ADMIN, Perfil.Rol.RECEPCIONISTA)
