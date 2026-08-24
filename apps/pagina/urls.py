from django.urls import path

from . import views



urlpatterns = [

    path(
        "",
        views.inicio,
        name="inicio"
    ),


    path(
        "nosotros/",
        views.nosotros,
        name="nosotros"
    ),


    path(
        "especialidades/",
        views.especialidades,
        name="especialidades"
    ),


    path(
        "medicos/",
        views.medicos,
        name="medicos"
    ),


    path(
        "servicios/",
        views.servicios,
        name="servicios"
    ),

    path(
        "precios/",
        views.precios,
        name="precios"
    ),


    path(
        "contacto/",
        views.contacto,
        name="contacto"
    ),

]
