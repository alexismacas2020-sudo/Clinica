import shutil
import tempfile
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.citas.models import Cita
from apps.especialidades.models import Especialidad
from apps.historial.models import HistorialClinico
from apps.medicos.models import Medico
from apps.usuarios.models import Perfil

from .models import Receta


MEDIA_TEMP = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_TEMP, ALLOWED_HOSTS=["testserver"])
class RecetasMedicoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMP, ignore_errors=True)

    def setUp(self):
        User = get_user_model()
        self.paciente = User.objects.create_user("paciente-receta", password="Clave123!")
        self.usuario_medico = User.objects.create_user("medico-receta", password="Clave123!")
        self.usuario_medico.perfil.rol = Perfil.Rol.MEDICO
        self.usuario_medico.perfil.save(update_fields=["rol"])
        especialidad = Especialidad.objects.create(nombre="Medicina receta")
        self.medico = Medico.objects.create(
            usuario=self.usuario_medico, especialidad=especialidad, nombres="Laura", apellidos="Médica",
            registro_profesional="REC-01",
        )
        self.cita = Cita.objects.create(
            paciente=self.paciente, medico=self.medico, especialidad=especialidad,
            fecha=timezone.localdate() + timedelta(days=1), hora="10:00", motivo="Control", estado=Cita.ATENDIDA,
        )
        self.historial = HistorialClinico.objects.create(
            cita=self.cita, medico=self.medico, paciente=self.paciente, motivo_consulta="Control",
            diagnostico="Diagnóstico", tratamiento="Tratamiento", finalizado=True,
        )

    def test_medico_guarda_receta_desde_historial_realizado(self):
        self.client.force_login(self.usuario_medico)
        response = self.client.post(reverse("recetas:emitir", args=[self.historial.pk]), {
            "diagnostico": "Diagnóstico", "medicamentos": "Medicamento A", "dosis": "500 mg",
            "frecuencia": "Cada 8 horas", "duracion": "5 días", "indicaciones": "Con alimentos",
            "observaciones": "Control posterior",
        })
        self.assertRedirects(response, reverse("historial:detalle_historial", args=[self.historial.pk]))
        receta = Receta.objects.get(historial=self.historial)
        self.assertTrue(receta.pdf.name.endswith(".pdf"))
        self.assertGreater(receta.pdf.size, 1000)

    def test_otro_usuario_no_emite_receta(self):
        self.client.force_login(self.paciente)
        self.assertEqual(self.client.get(reverse("recetas:emitir", args=[self.historial.pk])).status_code, 403)

    def test_no_permite_emitir_receta_despues_del_dia_de_atencion(self):
        HistorialClinico.objects.filter(pk=self.historial.pk).update(
            atendida_en=timezone.now() - timedelta(days=1)
        )
        self.client.force_login(self.usuario_medico)
        response = self.client.get(reverse("recetas:emitir", args=[self.historial.pk]))
        self.assertRedirects(response, reverse("historial:detalle_historial", args=[self.historial.pk]))
        self.assertFalse(Receta.objects.filter(historial=self.historial).exists())
