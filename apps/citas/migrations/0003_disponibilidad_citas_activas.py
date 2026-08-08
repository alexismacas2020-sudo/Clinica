from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0002_alter_cita_estado")]

    operations = [
        migrations.RemoveConstraint(model_name="cita", name="cita_medico_fecha_hora_unica"),
        migrations.AddConstraint(
            model_name="cita",
            constraint=models.UniqueConstraint(
                fields=("medico", "fecha", "hora"),
                condition=~models.Q(estado="CANCELADA"),
                name="cita_medico_fecha_hora_activa_unica",
            ),
        ),
    ]
