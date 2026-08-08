from django.contrib import admin

from .models import (
    Slider,
    Servicio,
    Testimonio
)



@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):

    list_display = (
        "titulo",
        "activo",
        "orden",
    )



@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):

    list_display = (
        "nombre",
        "activo",
    )



@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):

    list_display = (
        "nombre",
        "activo",
    )