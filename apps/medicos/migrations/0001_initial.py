import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("especialidades", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Medico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombres", models.CharField(max_length=100)),
                ("apellidos", models.CharField(max_length=100)),
                ("registro_profesional", models.CharField(max_length=50, unique=True)),
                ("foto", models.ImageField(blank=True, null=True, upload_to="medicos/")),
                ("biografia", models.TextField(blank=True)),
                ("consultorio", models.CharField(blank=True, max_length=100)),
                ("duracion_consulta", models.PositiveSmallIntegerField(default=30, help_text="Minutos")),
                ("activo", models.BooleanField(default=True)),
                ("destacado", models.BooleanField(default=False)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("especialidad", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="medicos", to="especialidades.especialidad")),
                ("usuario", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="medico", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("nombres", "apellidos"), "verbose_name": "Médico", "verbose_name_plural": "Médicos"},
        ),
    ]
