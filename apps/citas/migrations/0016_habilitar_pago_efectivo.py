from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0015_transferencia_como_unico_metodo")]

    operations = [
        migrations.AlterField(
            model_name="cita",
            name="metodo_pago",
            field=models.CharField(
                choices=[
                    ("TRANSFERENCIA", "Transferencia bancaria"),
                    ("EFECTIVO", "Efectivo en la clínica"),
                ],
                default="TRANSFERENCIA",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="cita",
            name="estado_pago",
            field=models.CharField(
                choices=[
                    ("NO_REQUERIDO", "No requiere pago"),
                    ("PENDIENTE", "Pago pendiente"),
                    ("EN_REVISION", "En revisión"),
                    ("APROBADO", "Pago realizado"),
                    ("RECHAZADO", "Rechazado"),
                ],
                default="NO_REQUERIDO",
                max_length=20,
            ),
        ),
    ]
