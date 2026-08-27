import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Crea o actualiza el administrador definido mediante variables de entorno."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_ADMIN_USERNAME", "").strip()
        email = os.environ.get("DJANGO_ADMIN_EMAIL", "").strip().lower()
        password = os.environ.get("DJANGO_ADMIN_PASSWORD", "")

        if not username or not email or not password:
            self.stdout.write(
                "Administrador omitido: configura DJANGO_ADMIN_USERNAME, "
                "DJANGO_ADMIN_EMAIL y DJANGO_ADMIN_PASSWORD."
            )
            return

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
            user.set_password(password)
            user.save()

            # La señal de usuarios crea el perfil; si ya existía, lo reactiva.
            perfil = getattr(user, "perfil", None)
            if perfil is not None and not perfil.activo:
                perfil.activo = True
                perfil.save(update_fields=["activo", "actualizado_en"])

        action = "creado" if created else "actualizado"
        self.stdout.write(self.style.SUCCESS(f"Administrador '{username}' {action}."))
