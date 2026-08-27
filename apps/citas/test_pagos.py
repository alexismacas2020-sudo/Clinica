from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.usuarios.models import Perfil

from .models import Banco, Cita


class FlujoPagosTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.paciente = User.objects.create_user("pago-paciente", email="pago@example.com", password="Clave123!")
        self.recepcion = User.objects.create_user("pago-recepcion", password="Clave123!")
        self.recepcion.perfil.rol = Perfil.Rol.RECEPCIONISTA
        self.recepcion.perfil.save(update_fields=["rol"])
        especialidad = Especialidad.objects.create(nombre="Pagos")
        self.medico = Medico.objects.create(especialidad=especialidad, nombres="Marta", apellidos="Pago", registro_profesional="PAGO-1")
        self.especialidad = especialidad
        self.banco = Banco.objects.create(nombre="Banco prueba", titular="Clínica", numero_cuenta="12345")
        self.fecha = timezone.localdate() + timedelta(days=1)
        while self.fecha.weekday() >= 5:
            self.fecha += timedelta(days=1)

    def test_paciente_puede_abrir_formulario_de_agendamiento(self):
        self.client.force_login(self.paciente)
        response = self.client.get(reverse("citas:agendar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Agenda tu cita")
        self.assertContains(response, self.banco.nombre)

    @patch("apps.citas.views.enviar_estado_pago")
    @patch("apps.citas.views.enviar_estado")
    def test_transferencia_comprobante_y_aprobacion(self, estado_email, pago_email):
        self.client.force_login(self.paciente)
        response = self.client.post(reverse("citas:agendar"), {
            "especialidad": self.especialidad.pk,
            "medico": self.medico.pk,
            "fecha": self.fecha.isoformat(),
            "hora": "15:00",
            "motivo": "Control",
            "metodo_pago": Cita.TRANSFERENCIA,
            "banco": self.banco.pk,
            "acepta_terminos": "on",
        })
        self.assertRedirects(response, reverse("citas:mis_citas"))
        cita = Cita.objects.get(paciente=self.paciente)
        self.assertEqual(cita.estado_pago, Cita.PAGO_PENDIENTE)

        archivo = SimpleUploadedFile("comprobante.pdf", b"%PDF-1.4 comprobante", content_type="application/pdf")
        response = self.client.post(reverse("citas:subir_comprobante", args=[cita.pk]), {"banco": self.banco.pk, "comprobante_pago": archivo})
        self.assertRedirects(response, reverse("citas:mis_citas"))
        cita.refresh_from_db()
        self.assertEqual(cita.estado_pago, Cita.EN_REVISION)
        self.assertTrue(cita.comprobante_pago)

        self.client.force_login(self.recepcion)
        response = self.client.post(reverse("citas:revisar_pago", args=[cita.pk]), {"decision": Cita.APROBADO, "observacion": "Verificado"})
        self.assertRedirects(response, reverse("dashboard:recepcionista"))
        cita.refresh_from_db()
        self.assertEqual(cita.estado_pago, Cita.APROBADO)
        self.assertEqual(cita.pago_revisado_por, self.recepcion)

    def test_transferencia_exige_banco(self):
        self.client.force_login(self.paciente)
        response = self.client.post(reverse("citas:agendar"), {
            "especialidad": self.especialidad.pk, "medico": self.medico.pk,
            "fecha": self.fecha.isoformat(), "hora": "16:00", "motivo": "Control",
            "metodo_pago": Cita.TRANSFERENCIA,
            "acepta_terminos": "on",
        })
        self.assertContains(response, "Selecciona la cuenta bancaria")
        self.assertFalse(Cita.objects.filter(paciente=self.paciente).exists())

    def test_agendamiento_exige_aceptar_terminos(self):
        self.client.force_login(self.paciente)
        response = self.client.post(reverse("citas:agendar"), {
            "especialidad": self.especialidad.pk,
            "medico": self.medico.pk,
            "fecha": self.fecha.isoformat(),
            "hora": "14:00",
            "motivo": "Control",
            "metodo_pago": Cita.EFECTIVO,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Debes aceptar los términos y condiciones")
        self.assertFalse(Cita.objects.filter(paciente=self.paciente).exists())

    def test_valor_consulta_por_defecto_es_treinta(self):
        cita = Cita(paciente=self.paciente, medico=self.medico, especialidad=self.especialidad, fecha=self.fecha, hora="17:00", motivo="Control")
        self.assertEqual(str(cita.valor_consulta), "30.00")

    def test_admin_puede_eliminar_banco_sin_pagos(self):
        admin = get_user_model().objects.create_superuser("pago-admin", email="admin@example.com", password="Clave123!")
        self.client.force_login(admin)
        response = self.client.post(reverse("citas:eliminar_banco", args=[self.banco.pk]))
        self.assertRedirects(response, reverse("citas:administrar_bancos"))
        self.assertFalse(Banco.objects.filter(pk=self.banco.pk).exists())
