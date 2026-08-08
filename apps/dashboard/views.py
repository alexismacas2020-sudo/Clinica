from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.usuarios.decorators import solo_administrador, solo_medico, solo_paciente, solo_recepcionista
from apps.usuarios.models import Perfil
from apps.usuarios.forms import CrearCredencialPersonalForm
from apps.citas.models import Cita
from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.historial.models import HistorialClinico
from apps.recetas.models import Receta


def _dashboard(request, template_name):
    return render(request, template_name, {"perfil": request.user.perfil})


@solo_administrador
def dashboard_admin(request):
    hoy = timezone.localdate()
    citas = Cita.objects.select_related("paciente", "medico", "especialidad")
    usuarios = get_user_model().objects.select_related("perfil")
    credencial_form = CrearCredencialPersonalForm(request.POST or None)
    if request.method == "POST" and request.POST.get("accion") == "crear_credencial":
        if credencial_form.is_valid():
            usuario = credencial_form.save()
            messages.success(
                request,
                f"Credenciales creadas para {usuario.get_full_name()} como {usuario.perfil.get_rol_display()}.",
            )
            return redirect("dashboard:admin")
        messages.error(request, "No se pudo crear la credencial. Revisa los campos señalados.")
    contexto = {
        "perfil": request.user.perfil,
        "credencial_form": credencial_form,
        "total_pacientes": usuarios.filter(perfil__rol=Perfil.Rol.PACIENTE, is_active=True).count(),
        "total_medicos": Medico.objects.filter(activo=True).count(),
        "total_recepcionistas": get_user_model().objects.filter(perfil__rol=Perfil.Rol.RECEPCIONISTA, is_active=True).count(),
        "total_especialidades": Especialidad.objects.filter(activo=True).count(),
        "citas_hoy": citas.filter(fecha=hoy).exclude(estado=Cita.CANCELADA).count(),
        "total_citas": citas.count(),
        "pendientes": citas.filter(estado=Cita.PENDIENTE).count(),
        "confirmadas": citas.filter(estado=Cita.CONFIRMADA).count(),
        "atendidas": citas.filter(estado=Cita.ATENDIDA).count(),
        "canceladas": citas.filter(estado=Cita.CANCELADA).count(),
        "citas_recientes": citas.order_by("-creado_en")[:6],
        "proximas_citas": citas.filter(fecha__gte=hoy).exclude(estado__in=[Cita.CANCELADA, Cita.ATENDIDA]).order_by("fecha", "hora")[:8],
        "ultimos_pacientes": usuarios.filter(perfil__rol=Perfil.Rol.PACIENTE).order_by("-date_joined")[:6],
    }
    return render(request, "dashboard/admin.html", contexto)


@solo_administrador
def crear_credencial(request):
    form = CrearCredencialPersonalForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(
            request,
            f"Credenciales creadas para {usuario.get_full_name()} como {usuario.perfil.get_rol_display()}.",
        )
        return redirect("usuarios:admin_usuario_detalle", pk=usuario.pk)
    if request.method == "POST":
        messages.error(request, "No se pudo crear la cuenta. Revisa los campos marcados.")
    return render(request, "dashboard/crear_credencial.html", {"form": form})


@solo_recepcionista
def dashboard_recepcionista(request):
    hoy = timezone.localdate()
    citas = Cita.objects.filter(fecha__gte=hoy).select_related("paciente", "medico", "especialidad")
    return render(request, "dashboard/recepcionista.html", {
        "perfil": request.user.perfil,
        "citas_hoy": citas.filter(fecha=hoy),
        "proximas_citas": citas[:20],
        "pendientes": citas.filter(estado__in=[Cita.PENDIENTE, Cita.REAGENDADA]).count(),
        "confirmadas_hoy": citas.filter(fecha=hoy, estado=Cita.CONFIRMADA).count(),
        "total_pacientes": get_user_model().objects.filter(perfil__rol=Perfil.Rol.PACIENTE, perfil__activo=True, is_active=True).count(),
    })


@solo_medico
def dashboard_medico(request):
    medico = Medico.objects.filter(usuario=request.user).first()
    citas = Cita.objects.none() if medico is None else Cita.objects.filter(medico=medico).select_related("paciente", "especialidad")
    historiales = HistorialClinico.objects.none() if medico is None else HistorialClinico.objects.filter(medico=medico, finalizado=True).select_related("paciente", "cita", "receta")
    return render(request, "dashboard/medico.html", {
        "perfil": request.user.perfil,
        "medico": medico,
        "citas_hoy": citas.filter(fecha=timezone.localdate()),
        "proximas_citas": citas.filter(fecha__gte=timezone.localdate()).exclude(estado__in=[Cita.ATENDIDA, Cita.CANCELADA])[:5],
        "historiales_recientes": historiales[:4],
        "total_realizadas": historiales.count(),
        "confirmadas_hoy": citas.filter(fecha=timezone.localdate(), estado=Cita.CONFIRMADA).count(),
        "recetas_guardadas": 0 if medico is None else Receta.objects.filter(medico=medico).count(),
    })


@solo_paciente
def dashboard_paciente(request):
    citas = Cita.objects.filter(paciente=request.user).select_related("medico", "especialidad")
    return render(request, "dashboard/paciente.html", {
        "perfil": request.user.perfil,
        "proxima_cita": citas.filter(fecha__gte=timezone.localdate()).exclude(estado=Cita.CANCELADA).first(),
        "historial": citas.order_by("-fecha", "-hora")[:5],
        "total_citas": citas.count(),
        "total_realizadas": citas.filter(estado=Cita.ATENDIDA).count(),
        "total_pendientes": citas.filter(estado__in=[Cita.PENDIENTE, Cita.REAGENDADA]).count(),
    })
