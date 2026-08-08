from django.contrib import admin

from .models import Especialidad


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo", "fecha_creacion")
    list_filter = ("activo",)
    search_fields = ("nombre", "descripcion")
