from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("configuracion", "0005_configuracion_contacto")]

    operations = [
        migrations.AddField(model_name="configuracioncontacto", name="facebook", field=models.URLField(blank=True, help_text="Enlace completo al perfil de Facebook", verbose_name="Facebook")),
        migrations.AddField(model_name="configuracioncontacto", name="instagram", field=models.URLField(blank=True, help_text="Enlace completo al perfil de Instagram", verbose_name="Instagram")),
        migrations.AddField(model_name="configuracioncontacto", name="whatsapp", field=models.URLField(blank=True, help_text="Ejemplo: https://wa.me/593999999999", verbose_name="WhatsApp")),
        migrations.AddField(model_name="configuracioncontacto", name="tiktok", field=models.URLField(blank=True, help_text="Enlace completo al perfil de TikTok", verbose_name="TikTok")),
        migrations.AddField(model_name="configuracioncontacto", name="youtube", field=models.URLField(blank=True, help_text="Enlace completo al canal de YouTube", verbose_name="YouTube")),
        migrations.AddField(model_name="configuracioncontacto", name="linkedin", field=models.URLField(blank=True, help_text="Enlace completo al perfil de LinkedIn", verbose_name="LinkedIn")),
    ]
