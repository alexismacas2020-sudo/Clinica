from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone

from apps.medicos.models import Medico
from apps.usuarios.decorators import administrador_o_recepcionista, solo_paciente, usuario_con_perfil_activo

from .forms import AgendarCitaForm, CitaRecepcionForm
from .models import Cita


def _horarios_libres(medico, fecha, excluir=None):
    hoy = timezone.localdate()
    ahora = timezone.localtime()
    minuto_actual = ahora.hour * 60 + ahora.minute
    if fecha < hoy or fecha.weekday() >= 5:
        return []
    ocupadas = Cita.objects.filter(medico=medico, fecha=fecha).exclude(estado=Cita.CANCELADA)
    if excluir:
        ocupadas = ocupadas.exclude(pk=excluir)
    ocupadas = {hora.strftime("%H:%M") for hora in ocupadas.values_list("hora", flat=True)}
    duracion = max(medico.duracion_consulta or 30, 15)
    horarios = []
    minuto = 8 * 60
    while minuto + duracion <= 18 * 60:
        valor = f"{minuto // 60:02d}:{minuto % 60:02d}"
        es_futuro = fecha > hoy or minuto > minuto_actual
        if valor not in ocupadas and es_futuro:
            horarios.append(valor)
        minuto += duracion
    return horarios


@usuario_con_perfil_activo
def medicos_por_especialidad(request):
    especialidad = request.GET.get("especialidad")
    medicos = Medico.objects.filter(activo=True)
    if especialidad:
        medicos = medicos.filter(especialidad_id=especialidad)
    return JsonResponse({"medicos": [
        {"id": medico.pk, "nombre": str(medico), "especialidad": medico.especialidad.nombre}
        for medico in medicos.select_related("especialidad")
    ]})


@usuario_con_perfil_activo
def calendario_disponibilidad(request):
    medico = get_object_or_404(Medico, pk=request.GET.get("medico"), activo=True)
    excluir = request.GET.get("excluir")
    fecha_texto = request.GET.get("fecha")
    if fecha_texto:
        try:
            fecha = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Fecha inválida."}, status=400)
        return JsonResponse({"fecha": fecha_texto, "horarios": _horarios_libres(medico, fecha, excluir)})
    hoy = timezone.localdate()
    fechas = []
    for desplazamiento in range(45):
        fecha = hoy + timedelta(days=desplazamiento)
        horarios = _horarios_libres(medico, fecha, excluir)
        if horarios:
            fechas.append({"fecha": fecha.isoformat(), "cupos": len(horarios)})
        if len(fechas) == 21:
            break
    return JsonResponse({"fechas": fechas, "duracion": medico.duracion_consulta})


@solo_paciente
def agendar(request):
    initial = {}
    if request.method == "GET":
        initial = {
            "especialidad": request.GET.get("especialidad"),
            "medico": request.GET.get("medico"),
        }
    form = AgendarCitaForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        cita = form.save(commit=False)
        cita.paciente = request.user
        cita.full_clean()
        cita.save()
        messages.success(request, "Tu cita fue registrada y está pendiente de confirmación.")
        return redirect("citas:mis_citas")
    return render(request, "citas/agendar.html", {"form": form})


@solo_paciente
def mis_citas(request):
    citas = Cita.objects.filter(paciente=request.user).select_related("medico", "especialidad")
    return render(request, "citas/mis_citas.html", {"citas": citas})


@administrador_o_recepcionista
def recepcion_crear(request):
    form = CitaRecepcionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cita = form.save()
        messages.success(request, f"Cita creada para {cita.paciente.get_full_name() or cita.paciente.username}.")
        return redirect("dashboard:recepcionista" if request.user.perfil.rol == "RECEPCIONISTA" else "dashboard:admin")
    return render(request, "citas/recepcion_form.html", {"form": form, "titulo": "Registrar cita"})


@administrador_o_recepcionista
def recepcion_editar(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    agenda_anterior = (cita.medico_id, cita.fecha, cita.hora)
    form = CitaRecepcionForm(request.POST or None, instance=cita)
    if request.method == "POST" and form.is_valid():
        cita = form.save(commit=False)
        agenda_nueva = (cita.medico_id, cita.fecha, cita.hora)
        if agenda_nueva != agenda_anterior:
            cita.estado = Cita.REAGENDADA
            mensaje = "La cita fue reagendada y quedó pendiente de nueva confirmación."
        else:
            mensaje = "Los datos de la cita fueron actualizados."
        cita.save()
        messages.success(request, mensaje)
        return redirect("dashboard:recepcionista")
    return render(request, "citas/recepcion_form.html", {"form": form, "titulo": "Reprogramar cita", "cita": cita})


@administrador_o_recepcionista
def verificar_disponibilidad(request):
    medico_id = request.GET.get("medico")
    fecha = request.GET.get("fecha")
    hora = request.GET.get("hora")
    excluir = request.GET.get("excluir")
    if not all((medico_id, fecha, hora)):
        return JsonResponse({"disponible": False, "mensaje": "Selecciona médico, fecha y hora."}, status=400)
    citas = Cita.objects.filter(medico_id=medico_id, fecha=fecha, hora=hora).exclude(estado=Cita.CANCELADA)
    if excluir:
        citas = citas.exclude(pk=excluir)
    disponible = not citas.exists()
    return JsonResponse({
        "disponible": disponible,
        "mensaje": "Horario disponible." if disponible else "Ese horario ya está ocupado. Elige otro.",
    })


@administrador_o_recepcionista
def cambiar_estado(request, pk, estado):
    if request.method != "POST":
        return redirect("dashboard:recepcionista")
    cita = get_object_or_404(Cita, pk=pk)
    estados_permitidos = {Cita.CONFIRMADA, Cita.CANCELADA}
    estado = estado.upper()
    if estado not in estados_permitidos:
        messages.error(request, "El estado solicitado no es válido.")
    else:
        cita.estado = estado
        cita.save(update_fields=["estado"])
        messages.success(request, f"La cita quedó {cita.get_estado_display().lower()}.")
    return redirect("dashboard:recepcionista")
