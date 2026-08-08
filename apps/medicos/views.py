from django.shortcuts import render

from .models import Medico


def lista(request):
    medicos = Medico.objects.filter(activo=True).select_related("especialidad")
    return render(request, "pagina/medicos.html", {"medicos": medicos})
