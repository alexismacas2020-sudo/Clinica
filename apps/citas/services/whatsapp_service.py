import logging

import requests
from django.conf import settings

from apps.usuarios.validators import normalizar_telefono_ecuador

logger = logging.getLogger(__name__)


class WhatsAppError(Exception):
    pass


def enviar_recordatorio(cita):
    token = settings.WHATSAPP_ACCESS_TOKEN
    phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
    if not token or not phone_id:
        raise WhatsAppError("La integración de WhatsApp no está configurada.")
    telefono = normalizar_telefono_ecuador(cita.paciente.perfil.telefono)
    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{phone_id}/messages"
    nombre = cita.paciente.get_full_name() or cita.paciente.username
    parametros = [
        nombre, settings.CLINICA_NOMBRE, cita.fecha.strftime("%d/%m/%Y"),
        cita.hora.strftime("%H:%M"), str(cita.medico), cita.especialidad.nombre,
        settings.CLINICA_DIRECCION,
    ]
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono.lstrip("+"),
        "type": "template",
        "template": {
            "name": settings.WHATSAPP_TEMPLATE_NAME,
            "language": {"code": settings.WHATSAPP_LANGUAGE_CODE},
            "components": [{"type": "body", "parameters": [
                {"type": "text", "text": valor} for valor in parametros
            ]}],
        },
    }
    try:
        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        mensaje = data.get("messages", [{}])[0]
        if not mensaje.get("id"):
            raise WhatsAppError("WhatsApp no devolvió un identificador de mensaje.")
        return {"message_id": mensaje["id"], "estado": mensaje.get("message_status", "accepted")}
    except requests.RequestException as exc:
        logger.warning("Falló el envío de un recordatorio de WhatsApp: %s", type(exc).__name__)
        raise WhatsAppError("No fue posible comunicarse con WhatsApp.") from exc
