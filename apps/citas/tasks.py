from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.usuarios.validators import normalizar_telefono_ecuador

from .models import Cita
from .services.whatsapp_service import WhatsAppError, enviar_recordatorio


@shared_task
def enviar_recordatorios_whatsapp():
    fecha_objetivo = timezone.localdate() + timedelta(days=1)
    ids = list(Cita.objects.filter(
        fecha=fecha_objetivo,
        estado__in=[Cita.PENDIENTE, Cita.CONFIRMADA],
        recordatorio_whatsapp_enviado=False,
    ).values_list("pk", flat=True))
    enviados = 0
    for cita_id in ids:
        with transaction.atomic():
            cita = Cita.objects.select_for_update().select_related(
                "paciente__perfil", "medico", "especialidad"
            ).get(pk=cita_id)
            if cita.recordatorio_whatsapp_enviado or cita.estado not in [Cita.PENDIENTE, Cita.CONFIRMADA]:
                continue
            try:
                normalizar_telefono_ecuador(cita.paciente.perfil.telefono)
                resultado = enviar_recordatorio(cita)
            except Exception as exc:
                mensaje = str(exc) if isinstance(exc, WhatsAppError) else "Número de WhatsApp inválido."
                cita.estado_recordatorio_whatsapp = "ERROR"
                cita.error_recordatorio_whatsapp = mensaje[:1000]
                cita.save(update_fields=["estado_recordatorio_whatsapp", "error_recordatorio_whatsapp"])
                continue
            cita.recordatorio_whatsapp_enviado = True
            cita.fecha_recordatorio_whatsapp = timezone.now()
            cita.whatsapp_message_id = resultado["message_id"]
            cita.estado_recordatorio_whatsapp = resultado["estado"][:30]
            cita.error_recordatorio_whatsapp = ""
            cita.save(update_fields=[
                "recordatorio_whatsapp_enviado", "fecha_recordatorio_whatsapp",
                "whatsapp_message_id", "estado_recordatorio_whatsapp", "error_recordatorio_whatsapp",
            ])
            enviados += 1
    return enviados
