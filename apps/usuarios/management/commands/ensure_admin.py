import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Crea o actualiza el administrador definido mediante variables de entorno."

    LOCAL_ADMIN_USERNAME = "ADMIN"
    LOCAL_ADMIN_EMAIL = "ADMIN@gmail.com"
    LOCAL_ADMIN_PASSWORD_HASH = (
        "pbkdf2_sha256$1200000$BmGw6l3b12ADoJZj98RGNB$"
        "cMdw1+ePzOGCwAqN2hhguatVb/IUV7shzv7rq/wCPmA="
    )

    def handle(self, *args, **options):
        username = os.environ.get(
            "DJANGO_ADMIN_USERNAME", self.LOCAL_ADMIN_USERNAME
        ).strip()
        email = os.environ.get(
            "DJANGO_ADMIN_EMAIL", self.LOCAL_ADMIN_EMAIL
        ).strip()
        password = os.environ.get("DJANGO_ADMIN_PASSWORD", "")

        User = get_user_model()
        with transaction.atomic():
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email},
            )
            user.email = email
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            if password:
                user.set_password(password)
            else:
                # Conserva la misma contraseña de la cuenta local transferida.
                user.password = self.LOCAL_ADMIN_PASSWORD_HASH
            user.save()

            # La señal de usuarios crea el perfil; si ya existía, lo reactiva.
            perfil = getattr(user, "perfil", None)
            if perfil is not None and not perfil.activo:
                perfil.activo = True
                perfil.save(update_fields=["activo", "actualizado_en"])

        action = "creado" if created else "actualizado"
        self.stdout.write(self.style.SUCCESS(f"Administrador '{username}' {action}."))
