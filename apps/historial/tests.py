import shutil
import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.citas.models import Cita
from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.recetas.models import Receta
from apps.usuarios.models import Perfil

from .models import HistorialClinico


MEDIA_TEMP = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_TEMP, ALLOWED_HOSTS=["testserver"])
class AtencionMedicaTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMP, ignore_errors=True)

    def setUp(self):
        User = get_user_model()
        self.paciente = User.objects.create_user("paciente-rx", password="Clave123!")
        self.usuario_medico = User.objects.create_user("medico-rx", password="Clave123!")
        self.usuario_medico.perfil.rol = Perfil.Rol.MEDICO; self.usuario_medico.perfil.save(update_fields=["rol"])
        self.otro_medico_user = User.objects.create_user("otro-medico", password="Clave123!")
        self.otro_medico_user.perfil.rol = Perfil.Rol.MEDICO; self.otro_medico_user.perfil.save(update_fields=["rol"])
        self.recepcion = User.objects.create_user("recepcion-rx", password="Clave123!")
        self.recepcion.perfil.rol = Perfil.Rol.RECEPCIONISTA; self.recepcion.perfil.save(update_fields=["rol"])
        esp = Especialidad.objects.create(nombre="Especialidad RX")
        self.medico = Medico.objects.create(usuario=self.usuario_medico, especialidad=esp, nombres="Ana", apellidos="Médica", registro_profesional="RX-01")
        Medico.objects.create(usuario=self.otro_medico_user, especialidad=esp, nombres="Otro", apellidos="Médico", registro_profesional="RX-02")
        self.cita = Cita.objects.create(paciente=self.paciente, medico=self.medico, especialidad=esp, fecha=timezone.localdate()+timedelta(days=1), hora="10:00", motivo="Dolor", estado=Cita.CONFIRMADA)
        self.data = {"motivo_consulta":"Dolor", "diagnostico":"Diagnóstico clínico", "tratamiento":"Reposo", "generar_receta":"on", "medicamentos":"Medicamento A", "dosis":"500 mg", "frecuencia":"Cada 8 horas", "duracion":"5 días", "indicaciones":"Tomar con alimentos"}

    def test_medico_asignado_finaliza_y_guarda_historial(self):
        self.client.force_login(self.usuario_medico)
        response = self.client.post(reverse("historial:atender_cita", args=[self.cita.pk]), self.data)
        self.assertRedirects(response, reverse("dashboard:medico"))
        self.cita.refresh_from_db(); self.assertEqual(self.cita.estado, Cita.ATENDIDA)
        historial = HistorialClinico.objects.get(cita=self.cita)
        self.assertTrue(historial.finalizado)
        self.assertFalse(Receta.objects.filter(cita=self.cita).exists())

    def test_medico_guarda_borrador_y_luego_continua(self):
        self.client.force_login(self.usuario_medico)
        response = self.client.post(reverse("historial:atender_cita", args=[self.cita.pk]), {
            "accion": "guardar_borrador", "motivo_consulta": "Dolor actualizado",
            "observaciones": "Pendiente de resultados",
        })
        self.assertRedirects(response, reverse("historial:atender_cita", args=[self.cita.pk]))
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.estado, Cita.CONFIRMADA)
        borrador = HistorialClinico.objects.get(cita=self.cita)
        self.assertFalse(borrador.finalizado)
        self.assertEqual(borrador.observaciones, "Pendiente de resultados")
        response = self.client.get(reverse("historial:atender_cita", args=[self.cita.pk]))
        self.assertContains(response, "Pendiente de resultados")

    def test_otro_medico_no_puede_atender(self):
        self.client.force_login(self.otro_medico_user)
        self.assertEqual(self.client.get(reverse("historial:atender_cita", args=[self.cita.pk])).status_code, 404)

    def test_recepcionista_no_puede_atender(self):
        self.client.force_login(self.recepcion)
        self.assertEqual(self.client.get(reverse("historial:atender_cita", args=[self.cita.pk])).status_code, 403)

    def test_finalizar_consulta_no_genera_receta(self):
        self.client.force_login(self.usuario_medico)
        self.client.post(reverse("historial:atender_cita", args=[self.cita.pk]), self.data)
        self.assertFalse(Receta.objects.filter(cita=self.cita).exists())

    def test_finalizar_y_emitir_receta_abre_el_formulario_de_receta(self):
        self.client.force_login(self.usuario_medico)
        datos = {**self.data, "accion": "finalizar_receta"}
        response = self.client.post(reverse("historial:atender_cita", args=[self.cita.pk]), datos)
        historial = HistorialClinico.objects.get(cita=self.cita)
        self.assertRedirects(response, reverse("recetas:emitir", args=[historial.pk]))
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.estado, Cita.ATENDIDA)
        self.assertTrue(historial.finalizado)

    def test_medico_consulta_solo_los_historiales_creados_por_el(self):
        self.client.force_login(self.usuario_medico)
        self.client.post(reverse("historial:atender_cita", args=[self.cita.pk]), self.data)
        historial = HistorialClinico.objects.get(cita=self.cita)
        listado = self.client.get(reverse("historial:mis_historiales"))
        self.assertContains(listado, self.paciente.username)
        self.assertEqual(self.client.get(reverse("historial:detalle_historial", args=[historial.pk])).status_code, 200)
        self.client.force_login(self.otro_medico_user)
        self.assertEqual(self.client.get(reverse("historial:detalle_historial", args=[historial.pk])).status_code, 404)
