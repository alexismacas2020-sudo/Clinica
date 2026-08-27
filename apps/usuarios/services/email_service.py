import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


class EmailError(Exception):
    pass


def enviar_correo(destinatario, asunto, mensaje, adjuntos=None):
    destinatario = (destinatario or "").strip()
    if not destinatario:
        raise EmailError("El destinatario no tiene un correo electrónico registrado.")
    if settings.EMAIL_BACKEND.lower().endswith("smtp.emailbackend") and (not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD):
        logger.error("Configuración SMTP incompleta: faltan EMAIL_HOST_USER o EMAIL_HOST_PASSWORD.")
        raise EmailError("El correo de la clínica no está configurado en el servidor.")
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
        logger.exception("Falló el envío SMTP (%s).", type(exc).__name__)
        raise EmailError("No fue posible enviar el correo desde Gmail.") from exc
