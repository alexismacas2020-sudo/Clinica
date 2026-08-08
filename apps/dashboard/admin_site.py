from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.citas.models import Cita
from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.usuarios.models import Perfil


class ClinicaAdminSite(AdminSite):
    site_header = "Clínica Reina · Administración"
    site_title = "Administración Clínica Reina"
    index_title = "Resumen administrativo"
    index_template = "admin/index.html"

    def index(self, request, extra_context=None):
        hoy = timezone.localdate()
        citas = Cita.objects.select_related("paciente", "medico", "especialidad")
        contexto = {
            "total_pacientes": get_user_model().objects.filter(perfil__rol=Perfil.Rol.PACIENTE, is_active=True).count(),
            "total_medicos": Medico.objects.filter(activo=True).count(),
            "total_especialidades": Especialidad.objects.filter(activo=True).count(),
            "citas_hoy": citas.filter(fecha=hoy).exclude(estado=Cita.CANCELADA).count(),
            "citas_pendientes": citas.filter(estado=Cita.PENDIENTE).count(),
            "citas_recientes": citas.order_by("-creado_en")[:5],
            "medicos_registrados": Medico.objects.select_related("especialidad", "usuario").order_by("nombres", "apellidos")[:8],
        }
        if extra_context:
            contexto.update(extra_context)
        return super().index(request, extra_context=contexto)


clinica_admin_site = ClinicaAdminSite(name="admin")

# Las aplicaciones ya registraron sus ModelAdmin en el sitio estándar durante
# el arranque de Django. Los registramos nuevamente en el sitio personalizado.
for modelo, modelo_admin in admin.site._registry.items():
    clinica_admin_site.register(modelo, modelo_admin.__class__)
