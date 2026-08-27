from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0014_cita_valor_consulta")]

    operations = [
        migrations.AlterField(
            model_name="cita",
            name="metodo_pago",
            field=models.CharField(
                choices=[("TRANSFERENCIA", "Transferencia bancaria")],
                default="TRANSFERENCIA",
                max_length=20,
            ),
        ),
    ]
