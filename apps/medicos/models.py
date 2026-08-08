from django.conf import settings
from django.db import models


class Medico(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medico",
    )
    especialidad = models.ForeignKey(
        "especialidades.Especialidad", on_delete=models.PROTECT, related_name="medicos"
    )
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    registro_profesional = models.CharField(max_length=50, unique=True)
    foto = models.ImageField(upload_to="medicos/", blank=True, null=True)
    biografia = models.TextField(blank=True)
    consultorio = models.CharField(max_length=100, blank=True)
    duracion_consulta = models.PositiveSmallIntegerField(default=30, help_text="Minutos")
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("nombres", "apellidos")
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self):
        return f"Dr(a). {self.nombres} {self.apellidos}"
