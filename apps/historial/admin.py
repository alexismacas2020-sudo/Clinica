from django.contrib import admin
from .models import ArchivoHistorial, HistorialClinico

@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ("cita", "paciente", "medico", "atendida_en")
    list_filter = ("medico__especialidad", "atendida_en")
    search_fields = ("paciente__username", "paciente__first_name", "paciente__last_name", "diagnostico")
    readonly_fields = ("cita", "paciente", "medico", "atendida_en", "actualizado_en")
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(ArchivoHistorial)
class ArchivoHistorialAdmin(admin.ModelAdmin):
    list_display = ("historial", "tipo", "subido_por", "creado_en")
    list_filter = ("tipo", "creado_en")
    search_fields = ("historial__paciente__username", "descripcion")
