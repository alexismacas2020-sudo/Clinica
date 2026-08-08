from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.historial.models import HistorialClinico
from apps.medicos.models import Medico
from apps.usuarios.decorators import solo_medico

from apps.usuarios.models import Perfil
from .models import Receta
from .forms import RecetaForm
from .services import generar_pdf_receta


@solo_medico
def emitir(request, historial_pk):
    medico = get_object_or_404(Medico, usuario=request.user, activo=True)
    historial = get_object_or_404(
        HistorialClinico.objects.select_related("cita", "paciente"),
        pk=historial_pk, medico=medico, finalizado=True, cita__estado="ATENDIDA",
    )
    if timezone.localdate(historial.atendida_en) != timezone.localdate():
        messages.error(request, "La receta debe emitirse el mismo día en que se finaliza la consulta.")
        return redirect("historial:detalle_historial", pk=historial.pk)
    existente = Receta.objects.filter(historial=historial).first()
    if existente:
        messages.info(request, "Esta consulta ya tiene una receta guardada.")
        return redirect("recetas:descargar", pk=existente.pk)
    nueva_receta = Receta(
        historial=historial, cita=historial.cita, paciente=historial.paciente, medico=medico,
        firma_digital=f"{medico} - Reg. {medico.registro_profesional}",
    )
    form = RecetaForm(request.POST or None, instance=nueva_receta, initial={"diagnostico": historial.diagnostico})
    if request.method == "POST" and form.is_valid():
        receta = form.save(commit=False)
        receta.full_clean()
        receta.save()
        url = request.build_absolute_uri(reverse("recetas:verificar", args=[receta.codigo_verificacion]))
        generar_pdf_receta(receta, url)
        messages.success(request, "Receta guardada y PDF generado correctamente.")
        return redirect("historial:detalle_historial", pk=historial.pk)
    return render(request, "recetas/emitir.html", {"form": form, "historial": historial})


def verificar(request, codigo):
    receta = get_object_or_404(Receta.objects.select_related("paciente", "medico", "medico__especialidad"), codigo_verificacion=codigo)
    return render(request, "recetas/verificar.html", {"receta": receta})


@login_required
def descargar(request, pk):
    receta = get_object_or_404(Receta.objects.select_related("medico", "paciente"), pk=pk)
    perfil = request.user.perfil
    permitido = request.user.is_superuser or perfil.rol == Perfil.Rol.ADMIN or receta.paciente_id == request.user.id or receta.medico.usuario_id == request.user.id
    if not permitido or not receta.pdf:
        raise Http404
    return FileResponse(receta.pdf.open("rb"), as_attachment=True, filename=f"receta-{receta.pk}.pdf")


@login_required
def mis_recetas(request):
    if request.user.perfil.rol != Perfil.Rol.PACIENTE:
        raise Http404
    recetas = Receta.objects.filter(paciente=request.user).select_related("medico", "historial", "cita")
    return render(request, "recetas/mis_recetas.html", {"recetas": recetas})
