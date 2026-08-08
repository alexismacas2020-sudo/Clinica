from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Perfil


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_o_sincronizar_perfil(sender, instance, created, **kwargs):
    perfil, _ = Perfil.objects.get_or_create(
        usuario=instance,
        defaults={"rol": Perfil.Rol.ADMIN if instance.is_superuser else Perfil.Rol.PACIENTE},
    )
    if instance.is_superuser and perfil.rol != Perfil.Rol.ADMIN:
        perfil.rol = Perfil.Rol.ADMIN
        perfil.save(update_fields=["rol", "actualizado_en"])
