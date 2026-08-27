from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.usuarios.services.email_service import EmailError, enviar_correo


class Command(BaseCommand):
    help = "Envía un correo real para comprobar la configuración SMTP del servidor."

    def add_arguments(self, parser):
        parser.add_argument(
            "--destinatario",
            default=settings.CONTACT_RECIPIENT_EMAIL,
            help="Correo que recibirá el mensaje de prueba.",
        )

    def handle(self, *args, **options):
        destinatario = options["destinatario"].strip()
        try:
            enviar_correo(
                destinatario,
                "Prueba de correo | Clínica Reina del Cisne",
                "La configuración SMTP funciona correctamente.",
            )
        except EmailError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Correo enviado correctamente a {destinatario}."))
