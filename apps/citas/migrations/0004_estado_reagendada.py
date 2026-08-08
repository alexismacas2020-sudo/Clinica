from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0003_disponibilidad_citas_activas")]

    operations = [
        migrations.AlterField(
            model_name="cita",
            name="estado",
            field=models.CharField(
                choices=[
                    ("PENDIENTE", "Pendiente"),
                    ("CONFIRMADA", "Confirmada"),
                    ("REAGENDADA", "Reagendada"),
                    ("ATENDIDA", "Atendida"),
                    ("CANCELADA", "Cancelada"),
                ],
                default="PENDIENTE",
                max_length=12,
            ),
        ),
    ]
