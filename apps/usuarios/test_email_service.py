from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from .services.email_service import EmailError, enviar_correo


@override_settings(
    EMAIL_PROVIDER="brevo",
    BREVO_API_URL="https://api.brevo.test/v3/smtp/email",
    BREVO_API_KEY="api-key-prueba",
    BREVO_SENDER_EMAIL="clinica@example.com",
    BREVO_SENDER_NAME="Clinica Reina del Cisne",
    EMAIL_TIMEOUT=10,
)
class BrevoEmailServiceTests(SimpleTestCase):
    @patch("apps.usuarios.services.email_service.requests.post")
    def test_envia_por_https_con_reply_to(self, post):
        respuesta = Mock()
        respuesta.raise_for_status.return_value = None
        respuesta.json.return_value = {"messageId": "mensaje-123"}
        post.return_value = respuesta

        resultado = enviar_correo(
            "paciente@example.com",
            "Cita confirmada",
            "Tu cita fue confirmada.",
            reply_to="contacto@example.com",
        )

        self.assertEqual(resultado["message_id"], "mensaje-123")
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["sender"]["email"], "clinica@example.com")
        self.assertEqual(payload["to"], [{"email": "paciente@example.com"}])
        self.assertEqual(payload["replyTo"], {"email": "contacto@example.com"})
        self.assertEqual(post.call_args.kwargs["timeout"], 10)

    @override_settings(BREVO_API_KEY="")
    def test_exige_api_key(self):
        with self.assertRaisesMessage(EmailError, "BREVO_API_KEY"):
            enviar_correo("paciente@example.com", "Asunto", "Mensaje")
