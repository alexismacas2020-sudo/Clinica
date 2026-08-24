from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("citas", "0010_banco_codigo_qr")]
    operations = [
        migrations.RenameField("cita", "recordatorio_whatsapp_enviado", "recordatorio_sms_enviado"),
        migrations.RenameField("cita", "fecha_recordatorio_whatsapp", "fecha_recordatorio_sms"),
        migrations.RenameField("cita", "whatsapp_message_id", "sms_message_id"),
        migrations.RenameField("cita", "estado_recordatorio_whatsapp", "estado_recordatorio_sms"),
        migrations.RenameField("cita", "error_recordatorio_whatsapp", "error_recordatorio_sms"),
    ]
