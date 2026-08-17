from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("citas", "0008_bancos_y_verificacion_pago")]

    operations = [
        migrations.RemoveField(model_name="cita", name="referencia_pago"),
    ]

