from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0004_perfil_cedula_telefono_unicos"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AlterField(model_name="perfil", name="telefono", field=models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name="Número celular")),
        migrations.CreateModel(
            name="CodigoRecuperacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo_hash", models.CharField(max_length=128)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("expira_en", models.DateTimeField()),
                ("usado_en", models.DateTimeField(blank=True, null=True)),
                ("intentos", models.PositiveSmallIntegerField(default=0)),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="codigos_recuperacion", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
