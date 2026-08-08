from django.contrib import admin

from .models import Medico


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("nombres", "apellidos", "especialidad", "registro_profesional", "activo", "destacado")
    list_filter = ("activo", "destacado", "especialidad")
    search_fields = ("nombres", "apellidos", "registro_profesional")
    list_select_related = ("especialidad", "usuario")
