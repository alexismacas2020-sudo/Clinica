from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("medicos", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="medico",
            name="foto_url",
            field=models.URLField(
                blank=True,
                help_text="URL directa de una imagen JPG, PNG o WEBP.",
                verbose_name="Enlace de la foto",
            ),
        ),
    ]
