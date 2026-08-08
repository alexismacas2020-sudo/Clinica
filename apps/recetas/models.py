import uuid

from django.core.exceptions import ValidationError
from django.db import models


class Receta(models.Model):
    ACTIVA = "ACTIVA"
    FINALIZADA = "FINALIZADA"
    ANULADA = "ANULADA"
    ESTADOS = ((ACTIVA, "Activa"), (FINALIZADA, "Finalizada"), (ANULADA, "Anulada"))

    historial = models.OneToOneField("historial.HistorialClinico", on_delete=models.PROTECT, related_name="receta")
    cita = models.OneToOneField("citas.Cita", on_delete=models.PROTECT, related_name="receta")
    paciente = models.ForeignKey("auth.User", on_delete=models.PROTECT, related_name="recetas")
    medico = models.ForeignKey("medicos.Medico", on_delete=models.PROTECT, related_name="recetas")
    diagnostico = models.TextField(max_length=3000)
    medicamentos = models.TextField(max_length=3000)
    dosis = models.TextField(max_length=1000)
    frecuencia = models.TextField(max_length=1000)
    duracion = models.CharField(max_length=500)
    indicaciones = models.TextField(max_length=3000)
    observaciones = models.TextField(max_length=2000, blank=True)
    firma_digital = models.CharField(max_length=500)
    codigo_verificacion = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pdf = models.FileField(upload_to="recetas/%Y/%m/", blank=True)
    estado = models.CharField(max_length=12, choices=ESTADOS, default=ACTIVA)
    emitida_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-emitida_en",)

    def clean(self):
        if not self.cita_id or not self.historial_id:
            raise ValidationError("La receta requiere una cita y un historial clínico.")
        if self.cita.estado != self.cita.ATENDIDA:
            raise ValidationError("Solo se permiten recetas para citas atendidas.")
        if self.historial.cita_id != self.cita_id:
            raise ValidationError("El historial no pertenece a esta cita.")
        if self.medico_id != self.cita.medico_id or self.paciente_id != self.cita.paciente_id:
            raise ValidationError("La receta debe usar el médico y paciente de la cita.")

    def __str__(self):
        return f"Receta {self.pk or 'nueva'} - {self.paciente}"
