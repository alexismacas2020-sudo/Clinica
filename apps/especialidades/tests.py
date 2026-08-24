from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.usuarios.models import Perfil

from .models import Especialidad


class GestionEspecialidadesTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user("admin-clinica", password="Clave123!")
        self.admin.perfil.rol = Perfil.Rol.ADMIN
        self.admin.perfil.save(update_fields=["rol"])
        self.client.force_login(self.admin)

    def test_admin_agrega_quita_y_elimina_especialidad(self):
        self.client.post(reverse("especialidades:administrar"), {
            "nombre": "Neurología", "descripcion": "Sistema nervioso", "activo": "on",
        })
        especialidad = Especialidad.objects.get(nombre="Neurología")
        self.client.post(reverse("especialidades:cambiar_activo", args=[especialidad.pk]))
        especialidad.refresh_from_db()
        self.assertFalse(especialidad.activo)
        self.client.post(reverse("especialidades:eliminar", args=[especialidad.pk]))
        self.assertFalse(Especialidad.objects.filter(pk=especialidad.pk).exists())

    def test_paciente_no_administra_especialidades(self):
        paciente = get_user_model().objects.create_user("paciente-esp", password="Clave123!")
        self.client.force_login(paciente)
        self.assertEqual(self.client.get(reverse("especialidades:administrar")).status_code, 403)

    def test_admin_puede_quitar_solo_la_foto_sin_eliminar_especialidad(self):
        especialidad = Especialidad.objects.create(
            nombre="Medicina deportiva", imagen="especialidades/medicina-deportiva.jpg"
        )
        respuesta = self.client.post(reverse("especialidades:quitar_imagen", args=[especialidad.pk]))
        especialidad.refresh_from_db()
        self.assertRedirects(respuesta, reverse("especialidades:administrar"))
        self.assertFalse(especialidad.imagen)
        self.assertTrue(Especialidad.objects.filter(pk=especialidad.pk).exists())
