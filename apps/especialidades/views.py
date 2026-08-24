from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from apps.usuarios.decorators import solo_administrador

from .forms import EspecialidadForm
from .models import Especialidad


@solo_administrador
def administrar(request):
    form = EspecialidadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La especialidad fue agregada correctamente.")
        return redirect("especialidades:administrar")
    return render(request, "especialidades/administrar.html", {
        "form": form,
        "especialidades": Especialidad.objects.all(),
    })


@solo_administrador
def editar(request, pk):
    especialidad = get_object_or_404(Especialidad, pk=pk)
    form = EspecialidadForm(request.POST or None, request.FILES or None, instance=especialidad)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La especialidad fue actualizada.")
        return redirect("especialidades:administrar")
    return render(request, "especialidades/editar.html", {"form": form, "especialidad": especialidad})


@solo_administrador
def quitar_imagen(request, pk):
    if request.method == "POST":
        especialidad = get_object_or_404(Especialidad, pk=pk)
        if especialidad.imagen:
            especialidad.imagen.delete(save=False)
            especialidad.imagen = None
            especialidad.save(update_fields=["imagen"])
            messages.success(request, f"La foto de {especialidad.nombre} fue eliminada.")
        else:
            messages.info(request, "Esta especialidad no tiene una foto asignada.")
    return redirect("especialidades:administrar")


@solo_administrador
def cambiar_activo(request, pk):
    if request.method == "POST":
        especialidad = get_object_or_404(Especialidad, pk=pk)
        especialidad.activo = not especialidad.activo
        especialidad.save(update_fields=["activo"])
        accion = "habilitada" if especialidad.activo else "quitada de las opciones de agenda"
        messages.success(request, f"La especialidad fue {accion}.")
    return redirect("especialidades:administrar")


@solo_administrador
def eliminar(request, pk):
    if request.method == "POST":
        especialidad = get_object_or_404(Especialidad, pk=pk)
        nombre = especialidad.nombre
        try:
            especialidad.delete()
            messages.success(request, f"La especialidad {nombre} fue eliminada.")
        except ProtectedError:
            messages.error(request, "No se puede eliminar porque tiene médicos o citas asociados. Puedes quitarla de la agenda desactivándola.")
    return redirect("especialidades:administrar")

# Create your views here.
