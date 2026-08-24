from django.conf import settings
from django.db import models
from django.utils import timezone


class Perfil(models.Model):
    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        RECEPCIONISTA = "RECEPCIONISTA", "Recepcionista"
        MEDICO = "MEDICO", "Médico"
        PACIENTE = "PACIENTE", "Paciente"

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.PACIENTE)
    cedula = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name="Cédula")
    telefono = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Número celular")
    foto = models.ImageField(upload_to="usuarios/", blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username

    @property
    def es_administrador(self):
        return self.rol == self.Rol.ADMIN or self.usuario.is_superuser


class CodigoRecuperacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="codigos_recuperacion")
    codigo_hash = models.CharField(max_length=128)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado_en = models.DateTimeField(null=True, blank=True)
    intentos = models.PositiveSmallIntegerField(default=0)

    @property
    def vigente(self):
        return self.usado_en is None and self.intentos < 5 and self.expira_en > timezone.now()
