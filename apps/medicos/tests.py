from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.citas.models import Cita
from apps.especialidades.models import Especialidad
from apps.usuarios.models import Perfil

from .models import Medico


class GestionMedicosTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user("admin-medicos", password="Clave123!")
        self.admin.perfil.rol = Perfil.Rol.ADMIN
        self.admin.perfil.save(update_fields=["rol"])
        self.usuario_medico = User.objects.create_user(
            "medico-editable", email="medico@clinica.test", password="Clave123!"
        )
        self.usuario_medico.perfil.rol = Perfil.Rol.MEDICO
        self.usuario_medico.perfil.save(update_fields=["rol"])
        self.especialidad, _ = Especialidad.objects.get_or_create(nombre="Cardiología")
        self.medico = Medico.objects.create(
            usuario=self.usuario_medico, especialidad=self.especialidad,
            nombres="Ana", apellidos="Mora", registro_profesional="MED-100",
        )
        self.client.force_login(self.admin)

    def test_admin_lista_y_edita_medico(self):
        respuesta = self.client.get(reverse("medicos:administrar"))
        self.assertContains(respuesta, "Ana Mora")
        respuesta = self.client.post(
            reverse("medicos:editar", args=[self.medico.pk]),
            {
                "nombres": "Ana María", "apellidos": "Mora",
                "especialidad": self.especialidad.pk,
                "registro_profesional": "MED-100", "consultorio": "204",
                "duracion_consulta": 30, "activo": "on",
            },
        )
        self.assertRedirects(respuesta, reverse("medicos:administrar"))
        self.medico.refresh_from_db()
        self.usuario_medico.refresh_from_db()
        self.assertEqual(self.medico.nombres, "Ana María")
        self.assertEqual(self.usuario_medico.first_name, "Ana María")

    def test_admin_quita_medico_sin_registros(self):
        respuesta = self.client.post(reverse("medicos:eliminar", args=[self.medico.pk]))
        self.assertRedirects(respuesta, reverse("medicos:administrar"))
        self.assertFalse(Medico.objects.filter(pk=self.medico.pk).exists())
        self.usuario_medico.refresh_from_db()
        self.assertFalse(self.usuario_medico.is_active)

    def test_medico_con_citas_se_desactiva_sin_borrar_historial(self):
        paciente = get_user_model().objects.create_user("paciente-medico", password="Clave123!")
        fecha = timezone.localdate() + timedelta(days=1)
        while fecha.weekday() >= 5:
            fecha += timedelta(days=1)
        Cita.objects.create(
            paciente=paciente, medico=self.medico, especialidad=self.especialidad,
            fecha=fecha, hora="08:00", motivo="Control",
        )
        self.client.post(reverse("medicos:eliminar", args=[self.medico.pk]))
        self.medico.refresh_from_db()
        self.assertFalse(self.medico.activo)
        self.assertTrue(Cita.objects.filter(medico=self.medico).exists())
