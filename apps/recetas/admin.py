from django.contrib import admin
from .models import Receta

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("id", "paciente", "medico", "emitida_en", "estado")
    list_filter = ("estado", "emitida_en", "medico__especialidad")
    search_fields = ("paciente__username", "paciente__first_name", "paciente__last_name", "codigo_verificacion")
    readonly_fields = ("historial", "cita", "paciente", "medico", "diagnostico", "medicamentos", "dosis", "frecuencia", "duracion", "indicaciones", "observaciones", "firma_digital", "codigo_verificacion", "pdf", "emitida_en")
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
