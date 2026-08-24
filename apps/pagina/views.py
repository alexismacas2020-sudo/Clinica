from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.configuracion.models import ConfiguracionContacto
from apps.citas.models import Cita
from .forms import ContactoForm



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


def precios(request):
    valor_consulta = Cita._meta.get_field("valor_consulta").get_default()
    return render(
        request,
        "pagina/precios.html",
        {
            "valor_consulta": valor_consulta,
            "especialidades": Especialidad.objects.filter(activo=True).order_by("nombre"),
        },
    )



def contacto(request):
    configuracion = ConfiguracionContacto.objects.filter(activo=True).order_by("pk").first()
    form = ContactoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        datos = form.cleaned_data
        cuerpo = (
            "Nuevo mensaje desde la página web de Clínica Reina del Cisne\n\n"
            f"Nombre: {datos['nombre']}\nCorreo: {datos['correo']}\nAsunto: {datos['asunto']}\n\n"
            f"Mensaje:\n{datos['mensaje']}"
        )
        try:
            EmailMessage(
                subject=f"Contacto web: {datos['asunto']}", body=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_RECIPIENT_EMAIL], reply_to=[datos["correo"]],
            ).send(fail_silently=False)
        except Exception:
            messages.error(request, "No pudimos enviar tu mensaje. Inténtalo nuevamente o escríbenos directamente.")
        else:
            messages.success(request, "Tu mensaje fue enviado correctamente. Te responderemos lo antes posible.")
            return redirect("pagina:contacto")
    return render(request, "pagina/contacto.html", {
        "contacto": configuracion or ConfiguracionContacto(), "form": form,
        "correo_contacto": settings.CONTACT_RECIPIENT_EMAIL,
    })
