from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Perfil
from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico


class UsuariosViewsTests(TestCase):
    def setUp(self):
        self.password = "ClaveSegura123!"
        self.usuario = get_user_model().objects.create_user(username="maria", email="maria@example.com", password=self.password)

    def test_usuario_nuevo_tiene_perfil_paciente(self):
        self.assertEqual(self.usuario.perfil.rol, Perfil.Rol.PACIENTE)

    def test_login_por_correo_redirige_a_dashboard_paciente(self):
        response = self.client.post(reverse("usuarios:login"), {"username": self.usuario.email, "password": self.password})
        self.assertRedirects(response, reverse("dashboard:paciente"))

    def test_registro_crea_paciente(self):
        response = self.client.post(reverse("usuarios:registro"), {"first_name": "Ana", "last_name": "Ruiz", "username": "ana", "cedula": "0102030405", "email": "ana@example.com", "telefono": "0987654321", "password1": self.password, "password2": self.password})
        usuario = get_user_model().objects.get(username="ana")
        self.assertEqual(usuario.perfil.rol, Perfil.Rol.PACIENTE)
        self.assertEqual(usuario.perfil.telefono, "+593987654321")
        self.assertRedirects(response, reverse("usuarios:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertIn("Tu cuenta fue creada correctamente", list(response.wsgi_request._messages)[0].message)

    def test_registro_rechaza_datos_duplicados_y_password_distinto(self):
        self.usuario.perfil.cedula = "1111111111"
        self.usuario.perfil.telefono = "+593999999999"
        self.usuario.perfil.save(update_fields=["cedula", "telefono"])
        response = self.client.post(reverse("usuarios:registro"), {
            "first_name": "Otra", "last_name": "Persona", "username": self.usuario.username,
            "cedula": "1111111111", "email": self.usuario.email, "telefono": "0999999999",
            "password1": "ClaveSegura123!", "password2": "OtraClave123!",
        })
        self.assertContains(response, "Este nombre de usuario ya está registrado")
        self.assertContains(response, "Este correo electrónico ya está en uso")
        self.assertContains(response, "La cédula ingresada ya está registrada")
        self.assertContains(response, "El número de WhatsApp ya está registrado")
        self.assertContains(response, "Los dos campos de contraseña no coinciden")

    def test_registro_rechaza_password_debil(self):
        response = self.client.post(reverse("usuarios:registro"), {
            "first_name": "Débil", "last_name": "Clave", "username": "debil",
            "cedula": "2222222222", "email": "debil@example.com", "telefono": "0977777777",
            "password1": "12345678", "password2": "12345678",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="debil").exists())

    def test_login_incorrecto_y_cuenta_desactivada_muestran_error(self):
        response = self.client.post(reverse("usuarios:login"), {"username": self.usuario.username, "password": "Incorrecta123!"})
        self.assertContains(response, "Usuario o contraseña incorrectos")
        self.usuario.is_active = False; self.usuario.save(update_fields=["is_active"])
        response = self.client.post(reverse("usuarios:login"), {"username": self.usuario.email, "password": self.password})
        self.assertContains(response, "Tu cuenta se encuentra desactivada")

    def test_superusuario_redirige_a_dashboard_admin(self):
        admin = get_user_model().objects.create_superuser(username="admin", email="admin@example.com", password=self.password)
        self.client.force_login(admin)
        response = self.client.get(reverse("usuarios:panel"))
        self.assertRedirects(response, reverse("dashboard:admin"))

    def test_paciente_no_accede_a_panel_medico(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("dashboard:medico")).status_code, 403)

    def test_logout_redirige_al_inicio(self):
        self.client.force_login(self.usuario)
        response = self.client.post(reverse("usuarios:logout"))
        self.assertRedirects(response, reverse("pagina:inicio"))

    def test_navbar_funciona_sin_google_configurado(self):
        self.assertEqual(self.client.get(reverse("pagina:inicio")).status_code, 200)

    def test_admin_crea_credenciales_de_recepcionista(self):
        admin = get_user_model().objects.create_superuser(username="admin2", email="admin2@example.com", password=self.password)
        self.client.force_login(admin)
        response = self.client.post(reverse("usuarios:crear_recepcionista"), {
            "nombres": "Rosa", "apellidos": "Díaz", "email": "rosa@example.com",
            "telefono": "0999999999", "password": self.password,
        })
        self.assertRedirects(response, reverse("usuarios:crear_recepcionista"))
        recepcionista = get_user_model().objects.get(email="rosa@example.com")
        self.assertEqual(recepcionista.perfil.rol, Perfil.Rol.RECEPCIONISTA)

    def test_admin_de_rol_crea_medico_desde_funcion_independiente(self):
        admin = get_user_model().objects.create_user("admin-medicos", password=self.password)
        admin.perfil.rol = Perfil.Rol.ADMIN
        admin.perfil.save(update_fields=["rol"])
        especialidad = Especialidad.objects.create(nombre="Medicina familiar")
        self.client.force_login(admin)
        response = self.client.post(reverse("usuarios:crear_medico"), {
            "nombres": "Carlos", "apellidos": "Rojas", "email": "carlos.medico@example.com",
            "especialidad": especialidad.pk, "registro_profesional": "MED-ADMIN-01",
            "consultorio": "101", "password": self.password,
        })
        self.assertRedirects(response, reverse("usuarios:crear_medico"))
        medico = Medico.objects.get(registro_profesional="MED-ADMIN-01")
        self.assertEqual(medico.usuario.perfil.rol, Perfil.Rol.MEDICO)

    def test_admin_gestiona_perfil_usuario_sin_django_admin(self):
        admin = get_user_model().objects.create_user("admin-perfiles", password=self.password)
        admin.perfil.rol = Perfil.Rol.ADMIN
        admin.perfil.save(update_fields=["rol"])
        self.client.force_login(admin)
        response = self.client.get(reverse("usuarios:admin_usuarios"))
        self.assertContains(response, self.usuario.username)
        response = self.client.post(reverse("usuarios:admin_usuario_editar", args=[self.usuario.pk]), {
            "nombres": "María", "apellidos": "Actualizada", "email": "maria.nueva@example.com",
            "telefono": "0966666666", "rol": Perfil.Rol.RECEPCIONISTA, "activo": "on",
        })
        self.assertRedirects(response, reverse("usuarios:admin_usuario_detalle", args=[self.usuario.pk]))
        self.usuario.refresh_from_db(); self.usuario.perfil.refresh_from_db()
        self.assertEqual(self.usuario.email, "maria.nueva@example.com")
        self.assertEqual(self.usuario.perfil.rol, Perfil.Rol.RECEPCIONISTA)

    def test_admin_no_puede_quitarse_rol_ni_desactivarse(self):
        admin = get_user_model().objects.create_user("admin-protegido", password=self.password)
        admin.perfil.rol = Perfil.Rol.ADMIN
        admin.perfil.save(update_fields=["rol"])
        self.client.force_login(admin)
        response = self.client.post(reverse("usuarios:admin_usuario_editar", args=[admin.pk]), {
            "nombres": "Admin", "apellidos": "Protegido", "email": "admin.protegido@example.com",
            "telefono": "", "rol": Perfil.Rol.PACIENTE,
        })
        self.assertEqual(response.status_code, 200)
        admin.refresh_from_db(); admin.perfil.refresh_from_db()
        self.assertTrue(admin.is_active)
        self.assertEqual(admin.perfil.rol, Perfil.Rol.ADMIN)
        self.client.post(reverse("usuarios:admin_usuario_estado", args=[admin.pk]))
        admin.refresh_from_db()
        self.assertTrue(admin.is_active)

    def test_paciente_no_accede_a_gestion_interna_de_usuarios(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("usuarios:admin_usuarios")).status_code, 403)
