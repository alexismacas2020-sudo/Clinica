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
    foto_url = models.URLField(
        blank=True,
        verbose_name="Enlace de la foto",
        help_text="URL directa de una imagen JPG, PNG o WEBP.",
    )
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

    @property
    def foto_publica(self):
        """Usa la foto médica y, para cuentas existentes, la foto del perfil."""
        if self.foto:
            return self.foto
        if self.usuario_id and hasattr(self.usuario, "perfil"):
            return self.usuario.perfil.foto
        return None

    @property
    def foto_src(self):
        """Devuelve una imagen visible sin exigir que el archivo esté alojado localmente."""
        foto = self.foto_publica
        if foto:
            return foto.url
        if self.foto_url:
            return self.foto_url

        primer_nombre = self.nombres.strip().split()[0].lower() if self.nombres.strip() else ""
        nombres_femeninos = {
            "ana", "andrea", "beatriz", "carmen", "carolina", "claudia", "daniela",
            "diana", "elena", "gabriela", "isabel", "laura", "lucia", "marcela",
            "maria", "marta", "monica", "natalia", "paola", "patricia", "rosa",
            "sofia", "valentina", "veronica",
        }
        if primer_nombre in nombres_femeninos:
            return "https://randomuser.me/api/portraits/women/44.jpg"
        return "https://randomuser.me/api/portraits/men/46.jpg"
