from django.urls import path

from . import views


app_name = "configuracion"

urlpatterns = [
    path("emergencias/", views.emergencias, name="emergencias"),
    path("contacto/", views.contacto, name="contacto"),
]
