from datetime import time, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.usuarios.models import Perfil
from .models import Cita


class FlujoEfectivoTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.paciente = User.objects.create_user("paciente-efectivo", email="efectivo@example.com", password="Clave123!")
        self.recepcion = User.objects.create_user("recepcion-efectivo", password="Clave123!")
        self.recepcion.perfil.rol = Perfil.Rol.RECEPCIONISTA
        self.recepcion.perfil.save(update_fields=["rol"])
        self.usuario_medico = User.objects.create_user("medico-efectivo", password="Clave123!")
        self.usuario_medico.perfil.rol = Perfil.Rol.MEDICO
        self.usuario_medico.perfil.save(update_fields=["rol"])
        especialidad = Especialidad.objects.create(nombre="Medicina de pagos")
        medico = Medico.objects.create(usuario=self.usuario_medico, especialidad=especialidad, nombres="Eva", apellidos="Cobro", registro_profesional="EFE-1")
        fecha = timezone.localdate() + timedelta(days=2)
        self.cita = Cita.objects.create(paciente=self.paciente, medico=medico, especialidad=especialidad, fecha=fecha, hora=time(10), motivo="Control", metodo_pago=Cita.EFECTIVO, estado=Cita.CONFIRMADA, estado_pago=Cita.PAGO_PENDIENTE)

    def test_pago_pendiente_bloquea_atencion(self):
        self.client.force_login(self.usuario_medico)
        self.assertRedirects(self.client.get(reverse("historial:atender_cita", args=[self.cita.pk])), reverse("dashboard:medico"))

    @patch("apps.citas.views.enviar_estado_pago")
    def test_recepcion_registra_efectivo(self, enviar):
        self.client.force_login(self.recepcion)
        self.client.post(reverse("citas:registrar_pago_efectivo", args=[self.cita.pk]))
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.estado_pago, Cita.APROBADO)

    def test_filtros_de_pagos_se_muestran_en_recepcion(self):
        self.client.force_login(self.recepcion)
        response = self.client.get(reverse("dashboard:recepcionista"), {"vista": "por_pagar"})
        self.assertContains(response, "Por pagar")
        self.assertContains(response, self.paciente.username)
        self.assertNotContains(response, "Reagendar")
