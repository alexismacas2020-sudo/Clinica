from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("citas", "0012_confirmacion_sms")]
    operations = [
        migrations.RenameField("cita", "recordatorio_sms_enviado", "recordatorio_email_enviado"),
        migrations.RenameField("cita", "fecha_recordatorio_sms", "fecha_recordatorio_email"),
        migrations.RenameField("cita", "estado_recordatorio_sms", "estado_recordatorio_email"),
        migrations.RenameField("cita", "error_recordatorio_sms", "error_recordatorio_email"),
        migrations.RenameField("cita", "confirmacion_sms_enviada", "confirmacion_email_enviada"),
        migrations.RenameField("cita", "fecha_confirmacion_sms", "fecha_confirmacion_email"),
        migrations.RenameField("cita", "error_confirmacion_sms", "error_confirmacion_email"),
        migrations.RemoveField("cita", "sms_message_id"),
        migrations.RemoveField("cita", "confirmacion_sms_message_id"),
    ]
