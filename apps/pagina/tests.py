from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.test import override_settings


class PaginaPreciosTests(TestCase):
    def test_pagina_de_precios_es_publica_y_muestra_tarifa(self):
        response = self.client.get(reverse("pagina:precios"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["valor_consulta"], Decimal("30.00"))
        self.assertContains(response, "no genera ninguna reserva")
        self.assertContains(response, "30,00")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="web@clinicareina.com",
    CONTACT_RECIPIENT_EMAIL="alexismacas2020@gmail.com",
)
class PaginaContactoTests(TestCase):
    def test_muestra_el_correo_de_contacto(self):
        response = self.client.get(reverse("pagina:contacto"))
        self.assertContains(response, "alexismacas2020@gmail.com")

    def test_formulario_envia_el_mensaje_al_correo_configurado(self):
        response = self.client.post(reverse("pagina:contacto"), {
            "nombre": "Paciente Prueba",
            "correo": "paciente@example.com",
            "asunto": "Información sobre citas",
            "mensaje": "Quisiera conocer los horarios disponibles.",
        })

        self.assertRedirects(response, reverse("pagina:contacto"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["alexismacas2020@gmail.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["paciente@example.com"])
