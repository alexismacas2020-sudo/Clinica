from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0016_habilitar_pago_efectivo")]

    operations = [
        migrations.AddField(
            model_name="banco",
            name="codigo_qr_url",
            field=models.URLField(
                blank=True,
                help_text="URL directa de una imagen JPG, PNG o WEBP.",
                verbose_name="Enlace de la imagen QR",
            ),
        ),
    ]
