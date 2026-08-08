from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0005_estado_realizada")]
    operations = [
        migrations.AddField(model_name="cita", name="recordatorio_whatsapp_enviado", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="cita", name="fecha_recordatorio_whatsapp", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="cita", name="whatsapp_message_id", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="cita", name="estado_recordatorio_whatsapp", field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name="cita", name="error_recordatorio_whatsapp", field=models.TextField(blank=True)),
    ]
