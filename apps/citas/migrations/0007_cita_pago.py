from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0006_recordatorio_whatsapp")]

    operations = [
        migrations.AddField(
            model_name="cita",
            name="metodo_pago",
            field=models.CharField(
                choices=[
                    ("EFECTIVO", "Efectivo en la clínica"),
                    ("TARJETA", "Tarjeta débito o crédito"),
                    ("TRANSFERENCIA", "Transferencia bancaria"),
                    ("SEGURO", "Seguro médico"),
                ],
                default="EFECTIVO",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="cita",
            name="referencia_pago",
            field=models.CharField(blank=True, max_length=120),
        ),
    ]

