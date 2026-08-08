import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("especialidades", "0001_initial"),
        ("medicos", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Cita",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField()),
                ("hora", models.TimeField()),
                ("motivo", models.TextField(max_length=500)),
                ("estado", models.CharField(choices=[("PENDIENTE", "Pendiente"), ("CONFIRMADA", "Confirmada"), ("CANCELADA", "Cancelada")], default="PENDIENTE", max_length=12)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("especialidad", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="citas", to="especialidades.especialidad")),
                ("medico", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="citas", to="medicos.medico")),
                ("paciente", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="citas", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("fecha", "hora")},
        ),
        migrations.AddConstraint(model_name="cita", constraint=models.UniqueConstraint(fields=("medico", "fecha", "hora"), name="cita_medico_fecha_hora_unica")),
    ]
