from django.contrib import admin

from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "paciente", "medico", "especialidad", "estado")
    list_filter = ("estado", "fecha", "especialidad")
    search_fields = ("paciente__username", "paciente__email", "medico__nombres", "medico__apellidos")
    list_select_related = ("paciente", "medico", "especialidad")
