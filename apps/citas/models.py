from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Cita(models.Model):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    ATENDIDA = "ATENDIDA"
    REAGENDADA = "REAGENDADA"
    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (CONFIRMADA, "Confirmada"),
        (REAGENDADA, "Reagendada"),
        (ATENDIDA, "Realizada"),
        (CANCELADA, "Cancelada"),
    ]

    paciente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="citas")
    medico = models.ForeignKey("medicos.Medico", on_delete=models.PROTECT, related_name="citas")
    especialidad = models.ForeignKey("especialidades.Especialidad", on_delete=models.PROTECT, related_name="citas")
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField(max_length=500)
    estado = models.CharField(max_length=12, choices=ESTADOS, default=PENDIENTE)
    creado_en = models.DateTimeField(auto_now_add=True)
    recordatorio_whatsapp_enviado = models.BooleanField(default=False)
    fecha_recordatorio_whatsapp = models.DateTimeField(null=True, blank=True)
    whatsapp_message_id = models.CharField(max_length=255, blank=True)
    estado_recordatorio_whatsapp = models.CharField(max_length=30, blank=True)
    error_recordatorio_whatsapp = models.TextField(blank=True)

    class Meta:
        ordering = ("fecha", "hora")
        constraints = [
            models.UniqueConstraint(
                fields=("medico", "fecha", "hora"),
                condition=~models.Q(estado="CANCELADA"),
                name="cita_medico_fecha_hora_activa_unica",
            )
        ]

    def clean(self):
        if self.fecha and self.fecha < date.today():
            raise ValidationError({"fecha": "No puedes agendar una cita en una fecha pasada."})
        if self.medico_id and self.especialidad_id and self.medico.especialidad_id != self.especialidad_id:
            raise ValidationError({"medico": "El médico seleccionado no pertenece a esta especialidad."})

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.medico}"
