from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0009_remove_referencia_pago")]

    operations = [
        migrations.AddField(
            model_name="banco",
            name="codigo_qr",
            field=models.ImageField(blank=True, upload_to="pagos/codigos_qr/", verbose_name="Código QR de pago"),
        ),
    ]

