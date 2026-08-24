import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("historial", "0002_borradores_atencion"), ("auth", "0012_alter_user_first_name_max_length")]
    operations = [
        migrations.CreateModel(
            name="ArchivoHistorial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("RADIOGRAFIA", "Radiografía"), ("LABORATORIO", "Resultado de laboratorio"), ("ECOGRAFIA", "Ecografía"), ("TOMOGRAFIA", "Tomografía"), ("RESONANCIA", "Resonancia"), ("OTRO", "Otro documento")], default="OTRO", max_length=20)),
                ("archivo", models.FileField(upload_to="historial/archivos/%Y/%m/")),
                ("descripcion", models.CharField(blank=True, max_length=250)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("historial", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="archivos", to="historial.historialclinico")),
                ("subido_por", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="archivos_clinicos_subidos", to="auth.user")),
            ],
            options={"verbose_name": "archivo clínico", "verbose_name_plural": "archivos clínicos", "ordering": ("-creado_en",)},
        ),
    ]
