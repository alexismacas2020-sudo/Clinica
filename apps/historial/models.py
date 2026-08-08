from django.core.exceptions import ValidationError
from django.db import models


class HistorialClinico(models.Model):
    cita = models.OneToOneField("citas.Cita", on_delete=models.PROTECT, related_name="historial_clinico")
    medico = models.ForeignKey("medicos.Medico", on_delete=models.PROTECT, related_name="historiales")
    paciente = models.ForeignKey("auth.User", on_delete=models.PROTECT, related_name="historiales_clinicos")
    motivo_consulta = models.TextField(max_length=1000, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Kilogramos")
    talla = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Metros")
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="°C")
    presion_arterial = models.CharField(max_length=20, blank=True)
    frecuencia_cardiaca = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Latidos por minuto")
    saturacion_oxigeno = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Porcentaje")
    diagnostico = models.TextField(max_length=3000, blank=True)
    tratamiento = models.TextField(max_length=3000, blank=True)
    observaciones = models.TextField(max_length=2000, blank=True)
    finalizado = models.BooleanField(default=False)
    atendida_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-atendida_en",)
        verbose_name = "Historial clínico"
        verbose_name_plural = "Historias clínicas"

    def clean(self):
        if self.cita_id:
            if self.medico_id != self.cita.medico_id or self.paciente_id != self.cita.paciente_id:
                raise ValidationError("El historial debe usar el médico y paciente de la cita.")

    def __str__(self):
        return f"Consulta {self.cita_id} - {self.paciente}"
