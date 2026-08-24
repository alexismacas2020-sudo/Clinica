from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("configuracion", "0004_activar_emergencias")]
    operations = [
        migrations.CreateModel(
            name="ConfiguracionContacto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(default="Siempre cerca de ti", max_length=120)),
                ("descripcion", models.CharField(default="Puedes comunicarte para solicitar orientación sobre servicios, especialistas y citas.", max_length=300)),
                ("telefono", models.CharField(default="0988128636", max_length=30)),
                ("correo", models.EmailField(default="contacto@clinicareina.com", max_length=254)),
                ("ubicacion", models.CharField(default="Loja, Ecuador", max_length=180)),
                ("horario", models.CharField(default="Lun–Vie 08:00–18:00", max_length=180)),
                ("enlace_mapa", models.URLField(blank=True)), ("activo", models.BooleanField(default=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
            ], options={"verbose_name": "configuración de contacto", "verbose_name_plural": "configuración de contacto"},
        ),
    ]
