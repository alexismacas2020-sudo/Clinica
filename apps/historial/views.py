from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.citas.models import Cita
from apps.medicos.models import Medico
from apps.usuarios.decorators import solo_medico

from .forms import AtencionMedicaForm
from .models import HistorialClinico


@solo_medico
def mis_historiales(request):
    medico = get_object_or_404(Medico, usuario=request.user, activo=True)
    historiales = HistorialClinico.objects.filter(medico=medico, finalizado=True).select_related(
        "paciente", "cita", "cita__especialidad"
    )
    busqueda = request.GET.get("q", "").strip()
    if busqueda:
        historiales = historiales.filter(
            Q(paciente__first_name__icontains=busqueda)
            | Q(paciente__last_name__icontains=busqueda)
            | Q(paciente__username__icontains=busqueda)
            | Q(diagnostico__icontains=busqueda)
        )
    return render(request, "historial/mis_historiales.html", {
        "medico": medico, "historiales": historiales, "busqueda": busqueda,
    })


@solo_medico
def detalle_historial(request, pk):
    medico = get_object_or_404(Medico, usuario=request.user, activo=True)
    historial = get_object_or_404(
        HistorialClinico.objects.select_related("paciente", "cita", "cita__especialidad"),
        pk=pk, medico=medico, finalizado=True,
    )
    return render(request, "historial/detalle_historial.html", {"historial": historial})


@solo_medico
def atender_cita(request, pk):
    medico = get_object_or_404(Medico, usuario=request.user, activo=True)
    cita = get_object_or_404(
        Cita.objects.select_related("paciente", "especialidad", "medico"),
        pk=pk, medico=medico,
    )
    if cita.estado == Cita.ATENDIDA:
        messages.info(request, "Esta consulta ya fue realizada.")
        return redirect("dashboard:medico")
    if cita.estado != Cita.CONFIRMADA:
        messages.error(request, "La cita debe estar confirmada antes de iniciar la atención.")
        return redirect("dashboard:medico")

    borrador = HistorialClinico.objects.filter(cita=cita, medico=medico).first()
    campos = (
        "motivo_consulta", "peso", "talla", "temperatura", "presion_arterial",
        "frecuencia_cardiaca", "saturacion_oxigeno", "diagnostico", "tratamiento", "observaciones",
    )
    initial = {"motivo_consulta": cita.motivo}
    if borrador:
        initial.update({campo: getattr(borrador, campo) for campo in campos})

    accion = request.POST.get("accion") if request.method == "POST" else None
    es_borrador = accion == "guardar_borrador"
    form = AtencionMedicaForm(request.POST or None, initial=initial, permitir_incompleto=es_borrador)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            datos = form.cleaned_data
            valores = {campo: datos.get(campo) for campo in campos}
            for campo in ("motivo_consulta", "presion_arterial", "diagnostico", "tratamiento", "observaciones"):
                valores[campo] = valores[campo] or ""
            valores.update({"medico": medico, "paciente": cita.paciente, "finalizado": not es_borrador})
            historial, _ = HistorialClinico.objects.update_or_create(cita=cita, defaults=valores)
            historial.full_clean()
            historial.save()
            if not es_borrador:
                cita.estado = Cita.ATENDIDA
                cita.save(update_fields=["estado"])
        if es_borrador:
            messages.success(request, "Borrador guardado. Puedes continuar la consulta más tarde.")
            return redirect("historial:atender_cita", pk=cita.pk)
        messages.success(request, "Consulta realizada e historial clínico guardado.")
        if accion == "finalizar_receta":
            return redirect("recetas:emitir", historial_pk=historial.pk)
        return redirect("dashboard:medico")
    return render(request, "historial/atender_cita.html", {"form": form, "cita": cita, "borrador": borrador})
