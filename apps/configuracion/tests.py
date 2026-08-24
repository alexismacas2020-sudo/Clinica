from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.usuarios.models import Perfil

from .models import ConfiguracionContacto, ConfiguracionEmergencia


class ConfiguracionEmergenciaTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user("admin-emergencias", password="Clave123!")
        self.admin.perfil.rol = Perfil.Rol.ADMIN
        self.admin.perfil.save(update_fields=["rol"])
        self.client.force_login(self.admin)

    def test_admin_crea_y_modifica_aviso_de_emergencia(self):
        respuesta = self.client.post(reverse("configuracion:emergencias"), {
            "titulo": "Emergencias 24 horas", "mensaje": "Llama inmediatamente si existe riesgo vital.",
            "telefono": "123", "activo": "on",
        })
        self.assertRedirects(respuesta, reverse("configuracion:emergencias"))
        configuracion = ConfiguracionEmergencia.objects.get()
        self.assertEqual(configuracion.telefono, "123")
        self.assertTrue(configuracion.activo)

        self.client.post(reverse("configuracion:emergencias"), {
            "titulo": configuracion.titulo, "mensaje": configuracion.mensaje, "telefono": "456",
        })
        configuracion.refresh_from_db()
        self.assertEqual(configuracion.telefono, "456")
        self.assertFalse(configuracion.activo)

    def test_paciente_no_puede_modificar_emergencias(self):
        paciente = get_user_model().objects.create_user("paciente-emergencias", password="Clave123!")
        self.client.force_login(paciente)
        self.assertEqual(self.client.get(reverse("configuracion:emergencias")).status_code, 403)

    def test_admin_modifica_contacto_y_se_publica(self):
        respuesta = self.client.post(reverse("configuracion:contacto"), {
            "titulo": "Contáctanos", "descripcion": "Estamos para ayudarte.",
            "telefono": "0988128636", "correo": "info@clinicareina.com",
            "ubicacion": "Loja, Ecuador", "horario": "Lunes a viernes",
            "enlace_mapa": "https://maps.google.com/", "activo": "on",
            "facebook": "https://facebook.com/clinicareina",
            "instagram": "https://instagram.com/clinicareina",
            "whatsapp": "https://wa.me/593988128636",
        })
        self.assertRedirects(respuesta, reverse("configuracion:contacto"))
        self.assertEqual(ConfiguracionContacto.objects.get().correo, "info@clinicareina.com")
        pagina = self.client.get(reverse("pagina:contacto"))
        self.assertContains(pagina, "alexismacas2020@gmail.com")
        inicio = self.client.get(reverse("pagina:inicio"))
        self.assertContains(inicio, "https://facebook.com/clinicareina")
        self.assertContains(inicio, "https://instagram.com/clinicareina")
        self.assertContains(inicio, "https://wa.me/593988128636")

    def test_paciente_no_puede_modificar_contacto(self):
        paciente = get_user_model().objects.create_user("paciente-contacto", password="Clave123!")
        self.client.force_login(paciente)
        self.assertEqual(self.client.get(reverse("configuracion:contacto")).status_code, 403)
