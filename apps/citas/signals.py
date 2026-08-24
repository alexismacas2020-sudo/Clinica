from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Cita


@receiver(pre_save, sender=Cita)
def reiniciar_recordatorio_al_reagendar(sender, instance, **kwargs):
    if not instance.pk:
        return
    anterior = Cita.objects.filter(pk=instance.pk).values("fecha", "hora").first()
    if anterior and (anterior["fecha"] != instance.fecha or anterior["hora"] != instance.hora):
        instance.recordatorio_email_enviado = False
        instance.fecha_recordatorio_email = None
        instance.estado_recordatorio_email = ""
        instance.error_recordatorio_email = ""
        instance.confirmacion_email_enviada = False
        instance.fecha_confirmacion_email = None
        instance.error_confirmacion_email = ""
