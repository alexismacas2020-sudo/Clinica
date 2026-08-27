from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.usuarios.models import Perfil
from apps.citas.models import Cita
from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from django.utils import timezone


class PermisosReportesTests(TestCase):
    def crear_usuario(self, nombre, rol):
        usuario = get_user_model().objects.create_user(nombre, password="Clave123!")
        usuario.perfil.rol = rol
        usuario.perfil.save(update_fields=["rol"])
        return usuario

    def test_admin_y_recepcionista_pueden_ver_reportes(self):
        for rol in (Perfil.Rol.ADMIN, Perfil.Rol.RECEPCIONISTA):
            with self.subTest(rol=rol):
                self.client.force_login(self.crear_usuario(f"usuario-{rol.lower()}", rol))
                self.assertEqual(self.client.get(reverse("reportes:resumen")).status_code, 200)

    def test_paciente_no_puede_ver_reportes(self):
        self.client.force_login(self.crear_usuario("paciente-reportes", Perfil.Rol.PACIENTE))
        self.assertEqual(self.client.get(reverse("reportes:resumen")).status_code, 403)

    def test_reporte_incluye_pago_en_efectivo_realizado(self):
        recepcion = self.crear_usuario("recepcion-reporte-efectivo", Perfil.Rol.RECEPCIONISTA)
        paciente = self.crear_usuario("paciente-reporte-efectivo", Perfil.Rol.PACIENTE)
        especialidad = Especialidad.objects.create(nombre="Reporte efectivo")
        medico = Medico.objects.create(especialidad=especialidad, nombres="Ana", apellidos="Caja", registro_profesional="REP-EFE")
        Cita.objects.create(
            paciente=paciente, medico=medico, especialidad=especialidad, fecha=timezone.localdate(),
            hora="10:00", motivo="Control", metodo_pago=Cita.EFECTIVO,
            estado_pago=Cita.APROBADO, valor_consulta="30.00",
        )
        self.client.force_login(recepcion)
        response = self.client.get(reverse("reportes:resumen"))
        self.assertEqual(response.context["ingresos_aprobados"], 30)
        self.assertContains(response, "Efectivo en la clínica")
