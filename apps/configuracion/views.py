from django.contrib import messages
from django.shortcuts import redirect, render

from apps.usuarios.decorators import solo_administrador

from .forms import ConfiguracionContactoForm, ConfiguracionEmergenciaForm
from .models import ConfiguracionContacto, ConfiguracionEmergencia


@solo_administrador
def emergencias(request):
    configuracion = ConfiguracionEmergencia.objects.order_by("pk").first()
    if configuracion is None:
        configuracion = ConfiguracionEmergencia()
    form = ConfiguracionEmergenciaForm(request.POST or None, instance=configuracion)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La información de emergencias fue actualizada.")
        return redirect("configuracion:emergencias")
    return render(request, "configuracion/emergencias.html", {"form": form, "configuracion": configuracion})


@solo_administrador
def contacto(request):
    configuracion = ConfiguracionContacto.objects.order_by("pk").first() or ConfiguracionContacto()
    form = ConfiguracionContactoForm(request.POST or None, instance=configuracion)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "La información de contacto fue actualizada.")
        return redirect("configuracion:contacto")
    return render(request, "configuracion/contacto.html", {"form": form, "configuracion": configuracion})
