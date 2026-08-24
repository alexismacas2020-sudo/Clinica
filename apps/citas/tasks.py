from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import Cita
from apps.usuarios.services.email_service import EmailError
from .services.email_service import enviar_recordatorio


@shared_task
def enviar_recordatorios_email():
    fecha_objetivo = timezone.localdate() + timedelta(days=1)
    ids = list(Cita.objects.filter(
        fecha=fecha_objetivo,
        estado__in=[Cita.PENDIENTE, Cita.CONFIRMADA],
        recordatorio_email_enviado=False,
    ).values_list("pk", flat=True))
    enviados = 0
    for cita_id in ids:
        with transaction.atomic():
            cita = Cita.objects.select_for_update().select_related(
                "paciente__perfil", "medico", "especialidad"
            ).get(pk=cita_id)
            if cita.recordatorio_email_enviado or cita.estado not in [Cita.PENDIENTE, Cita.CONFIRMADA]:
                continue
            try:
                if not cita.paciente.email:
                    raise EmailError("El paciente no tiene correo electrónico registrado.")
                resultado = enviar_recordatorio(cita)
            except Exception as exc:
                mensaje = str(exc) if isinstance(exc, EmailError) else "No se pudo preparar el correo."
                cita.estado_recordatorio_email = "ERROR"
                cita.error_recordatorio_email = mensaje[:1000]
                cita.save(update_fields=["estado_recordatorio_email", "error_recordatorio_email"])
                continue
            cita.recordatorio_email_enviado = True
            cita.fecha_recordatorio_email = timezone.now()
            cita.estado_recordatorio_email = resultado["estado"][:30]
            cita.error_recordatorio_email = ""
            cita.save(update_fields=[
                "recordatorio_email_enviado", "fecha_recordatorio_email",
                "estado_recordatorio_email", "error_recordatorio_email",
            ])
            enviados += 1
    return enviados
