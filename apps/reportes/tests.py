from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.usuarios.models import Perfil


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
