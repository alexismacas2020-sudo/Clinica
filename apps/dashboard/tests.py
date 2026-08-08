from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.usuarios.models import Perfil


class CredencialesDesdeDashboardTests(TestCase):
    def setUp(self):
        self.password = "ClaveSegura123!"
        self.admin = get_user_model().objects.create_superuser(
            "admin-dashboard", "admin@clinica.test", self.password
        )
        self.especialidad = Especialidad.objects.create(nombre="Medicina interna")
        self.client.force_login(self.admin)

    def test_crea_recepcionista_desde_dashboard(self):
        response = self.client.post(reverse("dashboard:admin"), {
            "accion": "crear_credencial", "rol": Perfil.Rol.RECEPCIONISTA,
            "nombres": "Laura", "apellidos": "Ruiz", "email": "laura@clinica.test",
            "telefono": "0999999999", "password": self.password,
        })
        self.assertRedirects(response, reverse("dashboard:admin"))
        usuario = get_user_model().objects.get(email="laura@clinica.test")
        self.assertEqual(usuario.perfil.rol, Perfil.Rol.RECEPCIONISTA)
        self.assertFalse(Medico.objects.filter(usuario=usuario).exists())

    def test_crea_medico_y_perfil_profesional_desde_dashboard(self):
        response = self.client.post(reverse("dashboard:admin"), {
            "accion": "crear_credencial", "rol": Perfil.Rol.MEDICO,
            "nombres": "Pedro", "apellidos": "Mora", "email": "pedro@clinica.test",
            "telefono": "0888888888", "password": self.password,
            "especialidad": self.especialidad.pk, "registro_profesional": "MED-900",
            "consultorio": "205",
        })
        self.assertRedirects(response, reverse("dashboard:admin"))
        usuario = get_user_model().objects.get(email="pedro@clinica.test")
        self.assertEqual(usuario.perfil.rol, Perfil.Rol.MEDICO)
        self.assertEqual(usuario.medico.especialidad, self.especialidad)

    def test_paciente_no_puede_crear_credenciales(self):
        paciente = get_user_model().objects.create_user("paciente-dashboard", password=self.password)
        self.client.force_login(paciente)
        self.assertEqual(self.client.get(reverse("dashboard:admin")).status_code, 403)

    def test_admin_de_rol_tambien_crea_credenciales(self):
        admin_rol = get_user_model().objects.create_user("admin-rol", password=self.password)
        admin_rol.perfil.rol = Perfil.Rol.ADMIN
        admin_rol.perfil.save(update_fields=["rol"])
        self.client.force_login(admin_rol)
        response = self.client.post(reverse("dashboard:admin"), {
            "accion": "crear_credencial", "rol": Perfil.Rol.RECEPCIONISTA,
            "nombres": "Sara", "apellidos": "López", "email": "sara@clinica.test",
            "telefono": "0961234567", "password": self.password,
        })
        self.assertRedirects(response, reverse("dashboard:admin"))
        self.assertEqual(get_user_model().objects.get(email="sara@clinica.test").perfil.rol, Perfil.Rol.RECEPCIONISTA)

    def test_registro_profesional_repetido_muestra_error_sin_crear_usuario(self):
        Medico.objects.create(
            especialidad=self.especialidad, nombres="Existente", apellidos="Prueba",
            registro_profesional="MED-REPETIDO",
        )
        response = self.client.post(reverse("dashboard:admin"), {
            "accion": "crear_credencial", "rol": Perfil.Rol.MEDICO,
            "nombres": "Nuevo", "apellidos": "Médico", "email": "nuevo@clinica.test",
            "password": self.password, "especialidad": self.especialidad.pk,
            "registro_profesional": "med-repetido",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ya existe un médico con este registro profesional")
        self.assertFalse(get_user_model().objects.filter(email="nuevo@clinica.test").exists())

    def test_acceso_rapido_credenciales_abre_pagina_y_crea_usuario(self):
        pagina = self.client.get(reverse("dashboard:crear_credencial"))
        self.assertEqual(pagina.status_code, 200)
        self.assertContains(pagina, "Crear credenciales")
        response = self.client.post(reverse("dashboard:crear_credencial"), {
            "rol": Perfil.Rol.RECEPCIONISTA, "nombres": "Diana", "apellidos": "Vega",
            "email": "diana@clinica.test", "telefono": "0961112233", "password": self.password,
        })
        usuario = get_user_model().objects.get(email="diana@clinica.test")
        self.assertRedirects(response, reverse("usuarios:admin_usuario_detalle", args=[usuario.pk]))

    def test_panel_muestra_accesos_rapidos_con_destinos_reales(self):
        response = self.client.get(reverse("dashboard:admin"))
        for destino in (
            reverse("usuarios:crear_medico"), reverse("especialidades:administrar"),
            reverse("dashboard:crear_credencial"), reverse("usuarios:admin_usuarios"),
            reverse("citas:recepcion_crear"), reverse("usuarios:perfil"),
        ):
            self.assertContains(response, f'href="{destino}"')


class EnlaceMiPanelTests(TestCase):
    def setUp(self):
        self.password = "ClaveSegura123!"

    def test_mi_panel_apunta_directamente_segun_el_rol(self):
        casos = [
            (Perfil.Rol.ADMIN, reverse("dashboard:admin")),
            (Perfil.Rol.RECEPCIONISTA, reverse("dashboard:recepcionista")),
            (Perfil.Rol.MEDICO, reverse("dashboard:medico")),
            (Perfil.Rol.PACIENTE, reverse("dashboard:paciente")),
        ]
        for indice, (rol, destino) in enumerate(casos):
            usuario = get_user_model().objects.create_user(f"panel-{indice}", password=self.password)
            usuario.perfil.rol = rol
            usuario.perfil.save(update_fields=["rol"])
            self.client.force_login(usuario)
            response = self.client.get(reverse("pagina:inicio"))
            self.assertContains(response, f'href="{destino}"')

    def test_dashboard_admin_usa_la_ruta_solicitada(self):
        self.assertEqual(reverse("dashboard:admin"), "/dashboard/")

    def test_admin_de_rol_inicia_sesion_y_va_a_dashboard(self):
        usuario = get_user_model().objects.create_user("admin-login", password=self.password)
        usuario.perfil.rol = Perfil.Rol.ADMIN
        usuario.perfil.save(update_fields=["rol"])
        response = self.client.post(reverse("usuarios:login"), {"username": usuario.username, "password": self.password})
        self.assertRedirects(response, "/dashboard/")
