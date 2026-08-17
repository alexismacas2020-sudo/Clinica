from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ConfiguracionEmergencia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(default="¿Tienes una emergencia?", max_length=100)),
                ("mensaje", models.CharField(default="Si hay riesgo vital, llama ahora. Nuestro equipo está disponible para orientarte.", max_length=280)),
                ("telefono", models.CharField(default="911", max_length=30)),
                ("whatsapp", models.CharField(blank=True, max_length=30)),
                ("activo", models.BooleanField(default=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "configuración de emergencias",
                "verbose_name_plural": "configuración de emergencias",
            },
        ),
    ]

