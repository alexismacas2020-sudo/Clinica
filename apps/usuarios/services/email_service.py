import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


class EmailError(Exception):
    pass


def enviar_correo(destinatario, asunto, mensaje, adjuntos=None):
    if settings.EMAIL_BACKEND.lower().endswith("smtp.emailbackend") and (not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD):
        raise EmailError("El correo de la clínica no está configurado.")
    try:
        correo = EmailMessage(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [destinatario])
        for nombre, contenido, tipo in adjuntos or []:
            correo.attach(nombre, contenido, tipo)
        if correo.send(fail_silently=False) != 1:
            raise EmailError("Gmail no confirmó el envío del correo.")
        return {"message_id": "", "estado": "sent"}
    except EmailError:
        raise
    except Exception as exc:
        logger.warning("Falló el envío de correo: %s", type(exc).__name__)
        raise EmailError("No fue posible enviar el correo desde Gmail.") from exc
