import logging
import smtplib
import socket

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.validators import validate_email

logger = logging.getLogger(__name__)


class EmailError(Exception):
    pass


def comprobar_configuracion_email():
    """Valida las variables necesarias sin enviar un mensaje."""
    if not settings.EMAIL_HOST:
        raise EmailError("Falta configurar EMAIL_HOST en el servidor.")
    if not settings.EMAIL_HOST_USER:
        raise EmailError("Falta configurar EMAIL_HOST_USER en el servidor.")
    if not settings.EMAIL_HOST_PASSWORD:
        raise EmailError("Falta configurar EMAIL_HOST_PASSWORD en el servidor.")
    if settings.EMAIL_USE_TLS and getattr(settings, "EMAIL_USE_SSL", False):
        raise EmailError("EMAIL_USE_TLS y EMAIL_USE_SSL no pueden estar activos al mismo tiempo.")


def enviar_correo(destinatario, asunto, mensaje, adjuntos=None):
    destinatario = (destinatario or "").strip()
    if not destinatario:
        raise EmailError("El destinatario no tiene un correo electrónico registrado.")
    try:
        validate_email(destinatario)
    except ValidationError as exc:
        raise EmailError("El correo electrónico del destinatario no es válido.") from exc

    if settings.EMAIL_BACKEND.lower().endswith("smtp.emailbackend"):
        comprobar_configuracion_email()

    try:
        conexion = get_connection(fail_silently=False, timeout=settings.EMAIL_TIMEOUT)
        correo = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            to=[destinatario],
            connection=conexion,
        )
        for nombre, contenido, tipo in adjuntos or []:
            correo.attach(nombre, contenido, tipo)
        if correo.send(fail_silently=False) != 1:
            raise EmailError("Gmail no confirmó la entrega del mensaje.")
        logger.info("Correo SMTP enviado correctamente a %s.", destinatario)
        return {"message_id": "", "estado": "sent"}
    except EmailError:
        raise
    except smtplib.SMTPAuthenticationError as exc:
        logger.exception("Gmail rechazó las credenciales SMTP.")
        raise EmailError("Gmail rechazó el usuario o la contraseña de aplicación.") from exc
    except (smtplib.SMTPException, socket.timeout, TimeoutError, OSError) as exc:
        logger.exception("Falló la conexión SMTP (%s).", type(exc).__name__)
        raise EmailError(
            "No fue posible conectar con Gmail. Revisa la configuración SMTP del servidor."
        ) from exc
    except Exception as exc:
        logger.exception("Falló el envío de correo (%s).", type(exc).__name__)
        raise EmailError("Ocurrió un error inesperado al enviar el correo.") from exc
