from django.shortcuts import render

from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico



def inicio(request):

    return render(
        request,
        "pagina/home.html"
    )



def nosotros(request):

    return render(
        request,
        "pagina/nosotros.html"
    )



def especialidades(request):

    return render(
        request,
        "pagina/especialidades.html",
        {"especialidades": Especialidad.objects.filter(activo=True)},
    )



def medicos(request):

    return render(
        request,
        "pagina/medicos.html",
        {"medicos": Medico.objects.filter(activo=True).select_related("especialidad", "usuario")},
    )



def servicios(request):

    return render(
        request,
        "pagina/servicios.html"
    )



def contacto(request):

    return render(
        request,
        "pagina/contacto.html"
    )
