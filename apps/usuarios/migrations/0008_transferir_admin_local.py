from django.db import migrations


ADMIN_PASSWORD_HASH = (
    "pbkdf2_sha256$1200000$BmGw6l3b12ADoJZj98RGNB$"
    "cMdw1+ePzOGCwAqN2hhguatVb/IUV7shzv7rq/wCPmA="
)


def transferir_admin_local(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Perfil = apps.get_model("usuarios", "Perfil")

    usuario, _ = User.objects.update_or_create(
        username="ADMIN",
        defaults={
            "email": "ADMIN@gmail.com",
            "password": ADMIN_PASSWORD_HASH,
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        },
    )
    Perfil.objects.update_or_create(
        usuario_id=usuario.pk,
        defaults={"rol": "ADMIN", "activo": True},
    )


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0007_normalizar_google_oauth")]
    operations = [
        migrations.RunPython(transferir_admin_local, migrations.RunPython.noop),
    ]
