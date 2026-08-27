from django.contrib import messages
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.usuarios.decorators import solo_administrador

from .forms import MedicoAdminForm
from .models import Medico


def lista(request):
    medicos = Medico.objects.filter(activo=True).select_related("especialidad")
    return render(request, "pagina/medicos.html", {"medicos": medicos})


@solo_administrador
def administrar(request):
    busqueda = request.GET.get("q", "").strip()
    medicos = Medico.objects.select_related("especialidad", "usuario").order_by(
        "nombres", "apellidos"
    )
    if busqueda:
        medicos = medicos.filter(
            Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(registro_profesional__icontains=busqueda)
            | Q(especialidad__nombre__icontains=busqueda)
        )
    return render(
        request,
        "medicos/administrar.html",
        {"medicos": medicos, "busqueda": busqueda},
    )


@solo_administrador
def editar(request, pk):
    medico = get_object_or_404(
        Medico.objects.select_related("especialidad", "usuario"), pk=pk
    )
    form = MedicoAdminForm(request.POST or None, request.FILES or None, instance=medico)
    if request.method == "POST" and form.is_valid():
        medico = form.save()
        if medico.usuario_id:
            usuario = medico.usuario
            usuario.first_name = medico.nombres
            usuario.last_name = medico.apellidos
            usuario.save(update_fields=["first_name", "last_name"])
        messages.success(request, "La información del médico fue actualizada.")
        return redirect("medicos:administrar")
    return render(request, "medicos/editar.html", {"form": form, "medico": medico})


@solo_administrador
def eliminar(request, pk):
    if request.method != "POST":
        return redirect("medicos:administrar")
    medico = get_object_or_404(Medico.objects.select_related("usuario"), pk=pk)
    nombre = str(medico)
    usuario = medico.usuario
    try:
        medico.delete()
    except ProtectedError:
        medico.activo = False
        medico.destacado = False
        medico.save(update_fields=["activo", "destacado"])
        if usuario:
            usuario.is_active = False
            usuario.save(update_fields=["is_active"])
            usuario.perfil.activo = False
            usuario.perfil.save(update_fields=["activo"])
        messages.warning(
            request,
            f"{nombre} tiene información clínica relacionada; se desactivó sin borrar su historial.",
        )
    else:
        if usuario:
            usuario.is_active = False
            usuario.save(update_fields=["is_active"])
            usuario.perfil.activo = False
            usuario.perfil.save(update_fields=["activo"])
        messages.success(request, f"{nombre} fue retirado del equipo médico.")
    return redirect("medicos:administrar")
