from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Cita


@receiver(pre_save, sender=Cita)
def reiniciar_recordatorio_al_reagendar(sender, instance, **kwargs):
    if not instance.pk:
        return
    anterior = Cita.objects.filter(pk=instance.pk).values("fecha", "hora").first()
    if anterior and (anterior["fecha"] != instance.fecha or anterior["hora"] != instance.hora):
        instance.recordatorio_whatsapp_enviado = False
        instance.fecha_recordatorio_whatsapp = None
        instance.whatsapp_message_id = ""
        instance.estado_recordatorio_whatsapp = ""
        instance.error_recordatorio_whatsapp = ""
