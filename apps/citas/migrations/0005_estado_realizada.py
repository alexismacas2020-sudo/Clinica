from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0004_estado_reagendada")]

    operations = [
        migrations.AlterField(
            model_name="cita",
            name="estado",
            field=models.CharField(
                choices=[
                    ("PENDIENTE", "Pendiente"),
                    ("CONFIRMADA", "Confirmada"),
                    ("REAGENDADA", "Reagendada"),
                    ("ATENDIDA", "Realizada"),
                    ("CANCELADA", "Cancelada"),
                ],
                default="PENDIENTE",
                max_length=12,
            ),
        ),
    ]
