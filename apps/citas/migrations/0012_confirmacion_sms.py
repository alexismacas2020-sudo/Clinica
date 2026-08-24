from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0011_rename_recordatorio_whatsapp_sms")]
    operations = [
        migrations.AddField(model_name="cita", name="confirmacion_sms_enviada", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="cita", name="fecha_confirmacion_sms", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="cita", name="confirmacion_sms_message_id", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="cita", name="error_confirmacion_sms", field=models.TextField(blank=True)),
    ]
