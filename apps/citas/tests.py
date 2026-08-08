from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch

from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.usuarios.models import Perfil

from .models import Cita
from .tasks import enviar_recordatorios_whatsapp


class RecepcionCitasTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.paciente = User.objects.create_user("paciente", password="Clave123!")
        self.recepcionista = User.objects.create_user("recepcion", password="Clave123!")
        self.recepcionista.perfil.rol = Perfil.Rol.RECEPCIONISTA
        self.recepcionista.perfil.save(update_fields=["rol"])
        self.especialidad = Especialidad.objects.create(nombre="Medicina de prueba")
        self.medico = Medico.objects.create(
            especialidad=self.especialidad,
            nombres="Mario",
            apellidos="Prueba",
            registro_profesional="TEST-001",
        )
        self.fecha = timezone.localdate() + timedelta(days=1)

    def test_paciente_no_accede_a_gestion_de_recepcion(self):
        self.client.force_login(self.paciente)
        self.assertEqual(self.client.get(reverse("citas:recepcion_crear")).status_code, 403)

    def test_recepcionista_crea_cita_para_paciente(self):
        self.client.force_login(self.recepcionista)
        response = self.client.post(reverse("citas:recepcion_crear"), {
            "paciente": self.paciente.pk,
            "especialidad": self.especialidad.pk,
            "medico": self.medico.pk,
            "fecha": self.fecha.isoformat(),
            "hora": "10:00",
            "motivo": "Control general",
        })
        self.assertRedirects(response, reverse("dashboard:recepcionista"))
        self.assertTrue(Cita.objects.filter(paciente=self.paciente, medico=self.medico).exists())

    def test_recepcionista_confirma_cita(self):
        cita = Cita.objects.create(paciente=self.paciente, especialidad=self.especialidad, medico=self.medico, fecha=self.fecha, hora="11:00", motivo="Control")
        self.client.force_login(self.recepcionista)
        self.client.post(reverse("citas:cambiar_estado", args=[cita.pk, "confirmada"]))
        cita.refresh_from_db()
        self.assertEqual(cita.estado, Cita.CONFIRMADA)

    def test_recepcionista_verifica_y_reagenda_solo_en_horario_disponible(self):
        cita = Cita.objects.create(paciente=self.paciente, especialidad=self.especialidad, medico=self.medico, fecha=self.fecha, hora="11:00", motivo="Control")
        ocupada = Cita.objects.create(paciente=self.paciente, especialidad=self.especialidad, medico=self.medico, fecha=self.fecha, hora="12:00", motivo="Otra")
        self.client.force_login(self.recepcionista)
        response = self.client.get(reverse("citas:verificar_disponibilidad"), {
            "medico": self.medico.pk, "fecha": self.fecha.isoformat(), "hora": "12:00", "excluir": cita.pk,
        })
        self.assertFalse(response.json()["disponible"])
        response = self.client.post(reverse("citas:recepcion_editar", args=[cita.pk]), {
            "paciente": self.paciente.pk, "especialidad": self.especialidad.pk, "medico": self.medico.pk,
            "fecha": self.fecha.isoformat(), "hora": "12:00", "motivo": "Control",
        })
        self.assertEqual(response.status_code, 200)
        cita.refresh_from_db()
        self.assertEqual(cita.hora.strftime("%H:%M"), "11:00")
        ocupada.estado = Cita.CANCELADA
        ocupada.save(update_fields=["estado"])
        response = self.client.post(reverse("citas:recepcion_editar", args=[cita.pk]), {
            "paciente": self.paciente.pk, "especialidad": self.especialidad.pk, "medico": self.medico.pk,
            "fecha": self.fecha.isoformat(), "hora": "12:00", "motivo": "Control",
        })
        self.assertRedirects(response, reverse("dashboard:recepcionista"))
        cita.refresh_from_db()
        self.assertEqual(cita.hora.strftime("%H:%M"), "12:00")
        self.assertEqual(cita.estado, Cita.REAGENDADA)

    def test_recepcionista_puede_confirmar_cita_reagendada(self):
        cita = Cita.objects.create(
            paciente=self.paciente, especialidad=self.especialidad, medico=self.medico,
            fecha=self.fecha, hora="13:00", motivo="Control", estado=Cita.REAGENDADA,
        )
        self.client.force_login(self.recepcionista)
        self.client.post(reverse("citas:cambiar_estado", args=[cita.pk, "confirmada"]))
        cita.refresh_from_db()
        self.assertEqual(cita.estado, Cita.CONFIRMADA)

    def test_calendario_muestra_solo_horas_libres(self):
        fecha = timezone.localdate() + timedelta(days=1)
        while fecha.weekday() >= 5:
            fecha += timedelta(days=1)
        Cita.objects.create(
            paciente=self.paciente, especialidad=self.especialidad, medico=self.medico,
            fecha=fecha, hora="08:00", motivo="Horario ocupado",
        )
        self.client.force_login(self.recepcionista)
        response = self.client.get(reverse("citas:calendario_disponibilidad"), {
            "medico": self.medico.pk, "fecha": fecha.isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("08:00", response.json()["horarios"])
        self.assertIn("08:30", response.json()["horarios"])

    def test_endpoint_filtra_medicos_por_especialidad(self):
        otra = Especialidad.objects.create(nombre="Otra especialidad")
        Medico.objects.create(especialidad=otra, nombres="Otro", apellidos="Doctor", registro_profesional="OTRO-1")
        self.client.force_login(self.recepcionista)
        response = self.client.get(reverse("citas:medicos_por_especialidad"), {"especialidad": self.especialidad.pk})
        ids = [item["id"] for item in response.json()["medicos"]]
        self.assertEqual(ids, [self.medico.pk])


class RecordatoriosWhatsAppTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.paciente = User.objects.create_user("paciente-wa", password="Clave123!")
        self.paciente.perfil.telefono = "+593987654321"
        self.paciente.perfil.save(update_fields=["telefono"])
        especialidad = Especialidad.objects.create(nombre="WhatsApp")
        self.medico = Medico.objects.create(especialidad=especialidad, nombres="Ana", apellidos="Médica", registro_profesional="WA-01")
        self.cita = Cita.objects.create(
            paciente=self.paciente, especialidad=especialidad, medico=self.medico,
            fecha=timezone.localdate() + timedelta(days=1), hora="09:00", motivo="Control", estado=Cita.CONFIRMADA,
        )

    @patch("apps.citas.tasks.enviar_recordatorio")
    def test_envio_exitoso_actualiza_cita_y_no_duplica(self, enviar):
        enviar.return_value = {"message_id": "wamid.123", "estado": "accepted"}
        self.assertEqual(enviar_recordatorios_whatsapp(), 1)
        self.cita.refresh_from_db()
        self.assertTrue(self.cita.recordatorio_whatsapp_enviado)
        self.assertEqual(self.cita.whatsapp_message_id, "wamid.123")
        self.assertEqual(enviar_recordatorios_whatsapp(), 0)
        self.assertEqual(enviar.call_count, 1)

    @patch("apps.citas.tasks.enviar_recordatorio")
    def test_cancelada_no_envia_y_fallo_queda_registrado(self, enviar):
        self.cita.estado = Cita.CANCELADA; self.cita.save(update_fields=["estado"])
        self.assertEqual(enviar_recordatorios_whatsapp(), 0)
        enviar.assert_not_called()
        self.cita.estado = Cita.CONFIRMADA; self.cita.save(update_fields=["estado"])
        enviar.side_effect = Exception("fallo simulado")
        self.assertEqual(enviar_recordatorios_whatsapp(), 0)
        self.cita.refresh_from_db()
        self.assertFalse(self.cita.recordatorio_whatsapp_enviado)
        self.assertEqual(self.cita.estado_recordatorio_whatsapp, "ERROR")

    def test_reagendar_reinicia_recordatorio(self):
        self.cita.recordatorio_whatsapp_enviado = True
        self.cita.whatsapp_message_id = "anterior"
        self.cita.save(update_fields=["recordatorio_whatsapp_enviado", "whatsapp_message_id"])
        self.cita.fecha += timedelta(days=1)
        self.cita.estado = Cita.REAGENDADA
        self.cita.save()
        self.cita.refresh_from_db()
        self.assertFalse(self.cita.recordatorio_whatsapp_enviado)
        self.assertEqual(self.cita.whatsapp_message_id, "")
