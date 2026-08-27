from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from datetime import datetime, timedelta
from django.utils import timezone

from apps.medicos.models import Medico
from apps.usuarios.decorators import administrador_o_recepcionista, solo_administrador, solo_paciente, usuario_con_perfil_activo

from .forms import AgendarCitaForm, BancoForm, CitaRecepcionForm, ComprobantePagoForm, RevisarPagoForm
from .models import Banco, Cita
from .services.email_service import enviar_estado, enviar_estado_pago
from apps.usuarios.services.email_service import EmailError


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
    horarios = []
    duracion = max(medico.duracion_consulta, 1)
    # Jornada de 08:00 a 13:00 y de 14:00 a 18:00.
    minutos_jornada = (
        *range(8 * 60, 13 * 60, duracion),
        *range(14 * 60, 18 * 60, duracion),
    )
    for minuto in minutos_jornada:
        hora, minutos = divmod(minuto, 60)
        valor = f"{hora:02d}:{minutos:02d}"
        es_futuro = fecha > hoy or minuto > minuto_actual
        if valor not in ocupadas and es_futuro:
            horarios.append(valor)
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
    form = AgendarCitaForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        cita = form.save(commit=False)
        cita.paciente = request.user
        cita.full_clean()
        cita.save()
        try:
            enviar_estado(cita)
        except EmailError as exc:
            messages.warning(request, f"La cita se registró, pero no fue posible enviar el correo. {exc}")
        if cita.metodo_pago == Cita.TRANSFERENCIA:
            try:
                enviar_estado_pago(cita)
            except EmailError:
                messages.warning(request, "No fue posible enviar el aviso del pago por correo.")
        messages.success(request, "Tu cita fue registrada y está pendiente de confirmación.")
        return redirect("citas:mis_citas")
    if request.method == "POST":
        messages.error(request, "No se pudo agendar la cita. Revisa los campos marcados y vuelve a intentarlo.")
    return render(request, "citas/agendar.html", {"form": form, "bancos": Banco.objects.filter(activo=True)})


@solo_paciente
def mis_citas(request):
    citas = Cita.objects.filter(paciente=request.user).select_related("medico", "especialidad", "banco")
    return render(request, "citas/mis_citas.html", {"citas": citas})


@administrador_o_recepcionista
def recepcion_crear(request):
    form = CitaRecepcionForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        cita = form.save()
        try:
            enviar_estado(cita)
        except EmailError:
            messages.warning(request, "La cita se creó, pero no fue posible enviar el correo.")
        messages.success(request, f"Cita creada para {cita.paciente.get_full_name() or cita.paciente.username}.")
        return redirect("dashboard:recepcionista" if request.user.perfil.rol == "RECEPCIONISTA" else "dashboard:admin")
    if request.method == "POST":
        messages.error(request, "No se pudo registrar la cita. Revisa los campos marcados.")
    return render(request, "citas/recepcion_form.html", {"form": form, "titulo": "Registrar cita", "bancos": Banco.objects.filter(activo=True)})


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
        estado_anterior = cita.estado
        cita.estado = estado
        cita.save(update_fields=["estado"])
        if estado == Cita.CONFIRMADA and estado_anterior != Cita.CONFIRMADA and not cita.confirmacion_email_enviada:
            try:
                if not cita.paciente.email:
                    raise EmailError("El paciente no tiene correo electrónico registrado.")
                enviar_estado(cita, estado_anterior)
                cita.confirmacion_email_enviada = True
                cita.fecha_confirmacion_email = timezone.now()
                cita.error_confirmacion_email = ""
                cita.save(update_fields=["confirmacion_email_enviada", "fecha_confirmacion_email", "error_confirmacion_email"])
                messages.success(request, "La cita quedó confirmada y el paciente recibió un correo.")
            except (EmailError, ValidationError) as exc:
                cita.error_confirmacion_email = str(exc)[:1000]
                cita.save(update_fields=["error_confirmacion_email"])
                messages.warning(
                    request,
                    f"La cita quedó confirmada, pero no fue posible enviar el correo al paciente. {exc}",
                )
        else:
            if estado == Cita.CANCELADA and estado_anterior != Cita.CANCELADA:
                try:
                    enviar_estado(cita, estado_anterior)
                except EmailError:
                    messages.warning(request, "La cita quedó cancelada, pero no fue posible enviar el correo.")
            messages.success(request, f"La cita quedó {cita.get_estado_display().lower()}.")
    return redirect("dashboard:recepcionista")


@solo_paciente
def subir_comprobante(request, pk):
    cita = get_object_or_404(Cita, pk=pk, paciente=request.user, metodo_pago=Cita.TRANSFERENCIA)
    if cita.estado_pago == Cita.APROBADO:
        messages.info(request, "Este pago ya fue aprobado.")
        return redirect("citas:mis_citas")
    form = ComprobantePagoForm(request.POST or None, request.FILES or None, instance=cita)
    if request.method == "POST" and form.is_valid():
        cita = form.save(commit=False)
        cita.estado_pago = Cita.EN_REVISION
        cita.observacion_pago = ""
        cita.pago_revisado_en = None
        cita.pago_revisado_por = None
        cita.save()
        try:
            enviar_estado_pago(cita)
        except EmailError:
            messages.warning(request, "El comprobante fue recibido, pero no se pudo enviar el correo.")
        messages.success(request, "Comprobante enviado para revisión.")
        return redirect("citas:mis_citas")
    return render(request, "citas/subir_comprobante.html", {"form": form, "cita": cita})


@administrador_o_recepcionista
def revisar_pago(request, pk):
    cita = get_object_or_404(Cita.objects.select_related("paciente", "banco"), pk=pk, metodo_pago=Cita.TRANSFERENCIA)
    if not cita.comprobante_pago:
        messages.error(request, "No se puede revisar un pago sin comprobante.")
        destino = "dashboard:admin" if request.user.is_superuser or request.user.perfil.es_administrador else "dashboard:recepcionista"
        return redirect(destino)
    form = RevisarPagoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cita.estado_pago = form.cleaned_data["decision"]
        cita.observacion_pago = form.cleaned_data["observacion"].strip()
        cita.pago_revisado_en = timezone.now()
        cita.pago_revisado_por = request.user
        cita.save(update_fields=["estado_pago", "observacion_pago", "pago_revisado_en", "pago_revisado_por"])
        try:
            enviar_estado_pago(cita)
        except EmailError:
            messages.warning(request, "El pago fue revisado, pero no se pudo enviar el correo.")
        messages.success(request, f"El pago quedó {cita.get_estado_pago_display().lower()}.")
        destino = "dashboard:admin" if request.user.is_superuser or request.user.perfil.es_administrador else "dashboard:recepcionista"
        return redirect(destino)
    return render(request, "citas/revisar_pago.html", {"form": form, "cita": cita})


@administrador_o_recepcionista
def registrar_pago_efectivo(request, pk):
    if request.method != "POST":
        messages.error(request, "La operación de pago solicitada no es válida.")
        return redirect("dashboard:recepcionista")
    cita = get_object_or_404(Cita.objects.select_related("paciente"), pk=pk, metodo_pago=Cita.EFECTIVO)
    if cita.estado in (Cita.CANCELADA, Cita.ATENDIDA):
        messages.error(request, "No se puede registrar el pago de una cita cancelada o ya realizada.")
        return redirect("dashboard:recepcionista")
    if cita.estado_pago == Cita.APROBADO:
        messages.info(request, "El pago en efectivo de esta cita ya estaba registrado.")
        return redirect("dashboard:recepcionista")
    cita.estado_pago = Cita.APROBADO
    cita.observacion_pago = "Pago en efectivo recibido en recepción."
    cita.pago_revisado_en = timezone.now()
    cita.pago_revisado_por = request.user
    cita.save(update_fields=["estado_pago", "observacion_pago", "pago_revisado_en", "pago_revisado_por"])
    try:
        enviar_estado_pago(cita)
    except EmailError:
        messages.warning(request, "El pago quedó registrado, pero no se pudo enviar el correo al paciente.")
    messages.success(request, "Pago en efectivo registrado. La cita ya puede ser atendida cuando esté confirmada.")
    return redirect("dashboard:recepcionista")


@solo_administrador
def administrar_bancos(request):
    form = BancoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cuenta bancaria guardada.")
        return redirect("citas:administrar_bancos")
    return render(request, "citas/bancos.html", {"form": form, "bancos": Banco.objects.all()})


@solo_administrador
def editar_banco(request, pk):
    banco = get_object_or_404(Banco, pk=pk)
    form = BancoForm(request.POST or None, request.FILES or None, instance=banco)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cuenta bancaria actualizada.")
        return redirect("citas:administrar_bancos")
    return render(request, "citas/banco_editar.html", {"form": form, "banco": banco})


@solo_administrador
def eliminar_banco(request, pk):
    banco = get_object_or_404(Banco, pk=pk)
    if request.method == "POST":
        try:
            banco.delete()
            messages.success(request, "Cuenta bancaria eliminada.")
        except ProtectedError:
            banco.activo = False
            banco.save(update_fields=["activo"])
            messages.warning(request, "La cuenta tiene pagos asociados; se desactivó para conservar el historial.")
    return redirect("citas:administrar_bancos")
