import logging
import smtplib
import socket
import base64

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.validators import validate_email

logger = logging.getLogger(__name__)


class EmailError(Exception):
    pass


def comprobar_configuracion_email():
    """Valida las variables necesarias sin enviar un mensaje."""
    proveedor = getattr(settings, "EMAIL_PROVIDER", "smtp").lower()
    if proveedor == "brevo":
        if not settings.BREVO_API_KEY:
            raise EmailError("Falta configurar BREVO_API_KEY en el servidor.")
        if not settings.BREVO_SENDER_EMAIL:
            raise EmailError("Falta configurar BREVO_SENDER_EMAIL en el servidor.")
        try:
            validate_email(settings.BREVO_SENDER_EMAIL)
        except ValidationError as exc:
            raise EmailError("BREVO_SENDER_EMAIL no es un correo valido.") from exc
        return
    if proveedor != "smtp":
        raise EmailError(f"EMAIL_PROVIDER no soportado: {proveedor}.")
    if not settings.EMAIL_HOST:
        raise EmailError("Falta configurar EMAIL_HOST en el servidor.")
    if not settings.EMAIL_HOST_USER:
        raise EmailError("Falta configurar EMAIL_HOST_USER en el servidor.")
    if not settings.EMAIL_HOST_PASSWORD:
        raise EmailError("Falta configurar EMAIL_HOST_PASSWORD en el servidor.")
    if settings.EMAIL_USE_TLS and getattr(settings, "EMAIL_USE_SSL", False):
        raise EmailError("EMAIL_USE_TLS y EMAIL_USE_SSL no pueden estar activos al mismo tiempo.")


def _enviar_con_brevo(destinatario, asunto, mensaje, adjuntos=None, reply_to=None):
    payload = {
        "sender": {"email": settings.BREVO_SENDER_EMAIL, "name": settings.BREVO_SENDER_NAME},
        "to": [{"email": destinatario}],
        "subject": asunto,
        "textContent": mensaje,
    }
    if reply_to:
        payload["replyTo"] = {"email": reply_to}
    if adjuntos:
        payload["attachment"] = [
            {"name": nombre, "content": base64.b64encode(contenido).decode("ascii")}
            for nombre, contenido, _tipo in adjuntos
        ]
    try:
        respuesta = requests.post(
            settings.BREVO_API_URL,
            headers={"accept": "application/json", "api-key": settings.BREVO_API_KEY},
            json=payload,
            timeout=settings.EMAIL_TIMEOUT,
        )
        respuesta.raise_for_status()
    except requests.Timeout as exc:
        raise EmailError("La API de correo no respondio a tiempo.") from exc
    except requests.RequestException as exc:
        detalle = ""
        if exc.response is not None:
            try:
                detalle = exc.response.json().get("message", "")
            except (ValueError, AttributeError):
                pass
        logger.exception("Brevo rechazo el correo: %s", detalle or type(exc).__name__)
        raise EmailError(
            f"Brevo rechazo el correo: {detalle}"
            if detalle else "No fue posible conectar con la API de correo."
        ) from exc
    try:
        message_id = respuesta.json().get("messageId", "")
    except ValueError:
        message_id = ""
    logger.info("Correo enviado por Brevo a %s (id=%s).", destinatario, message_id)
    return {"message_id": message_id, "estado": "sent"}


def enviar_correo(destinatario, asunto, mensaje, adjuntos=None, reply_to=None):
    destinatario = (destinatario or "").strip()
    if not destinatario:
        raise EmailError("El destinatario no tiene un correo electrónico registrado.")
    try:
        validate_email(destinatario)
    except ValidationError as exc:
        raise EmailError("El correo electrónico del destinatario no es válido.") from exc

    proveedor = getattr(settings, "EMAIL_PROVIDER", "smtp").lower()
    usa_backend_smtp = settings.EMAIL_BACKEND.lower().endswith("smtp.emailbackend")
    if proveedor != "smtp" or usa_backend_smtp:
        comprobar_configuracion_email()

    if reply_to:
        reply_to = reply_to.strip()
        try:
            validate_email(reply_to)
        except ValidationError as exc:
            raise EmailError("El correo de respuesta no es valido.") from exc

    if proveedor == "brevo":
        return _enviar_con_brevo(
            destinatario, asunto, mensaje, adjuntos=adjuntos, reply_to=reply_to
        )

    try:
        conexion = get_connection(fail_silently=False, timeout=settings.EMAIL_TIMEOUT)
        correo = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            to=[destinatario],
            reply_to=[reply_to] if reply_to else None,
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
