from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("configuracion", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="ConfiguracionPaginaPrincipal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("distintivo", models.CharField(default="Cuidado médico de confianza", max_length=100)),
                ("titulo", models.CharField(default="Tu salud está en las mejores manos", max_length=180)),
                ("descripcion", models.CharField(default="Contamos con médicos especialistas, tecnología moderna y atención personalizada para cuidar de ti y tu familia.", max_length=320)),
                ("boton_principal", models.CharField(default="Agendar cita", max_length=60)),
                ("boton_secundario", models.CharField(default="Contactar", max_length=60)),
                ("pacientes_cifra", models.PositiveIntegerField(default=5000)),
                ("pacientes_texto", models.CharField(default="Pacientes atendidos", max_length=80)),
                ("medicos_cifra", models.PositiveIntegerField(default=50)),
                ("medicos_texto", models.CharField(default="Médicos especialistas", max_length=80)),
                ("experiencia_cifra", models.PositiveIntegerField(default=15)),
                ("experiencia_texto", models.CharField(default="Años de experiencia", max_length=80)),
                ("especialidades_cifra", models.PositiveIntegerField(default=20)),
                ("especialidades_texto", models.CharField(default="Especialidades", max_length=80)),
                ("titulo_especialidades", models.CharField(default="Especialidades médicas", max_length=120)),
                ("descripcion_especialidades", models.CharField(default="Profesionales preparados para cuidar tu salud en cada etapa.", max_length=220)),
                ("titulo_medicos", models.CharField(default="Médicos que cuidan de ti", max_length=120)),
                ("descripcion_medicos", models.CharField(default="Especialistas comprometidos con tu bienestar y una atención cercana.", max_length=220)),
                ("titulo_servicios", models.CharField(default="Nuestros servicios", max_length=120)),
                ("descripcion_servicios", models.CharField(default="Soluciones pensadas para ofrecerte una experiencia de salud ágil y completa.", max_length=220)),
                ("titulo_cta", models.CharField(default="Agenda una consulta con nuestros especialistas", max_length=160)),
                ("texto_cta", models.CharField(default="Tu bienestar comienza hoy", max_length=80)),
                ("mostrar_estadisticas", models.BooleanField(default=True)),
                ("mostrar_especialidades", models.BooleanField(default=True)),
                ("mostrar_medicos", models.BooleanField(default=True)),
                ("mostrar_servicios", models.BooleanField(default=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "página principal",
                "verbose_name_plural": "página principal",
            },
        ),
    ]

