import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "__first__"),
        ("citas", "0007_cita_pago"),
    ]

    operations = [
        migrations.CreateModel(
            name="Banco",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100, unique=True)),
                ("titular", models.CharField(max_length=140)),
                ("numero_cuenta", models.CharField(max_length=50)),
                ("tipo_cuenta", models.CharField(default="Cuenta corriente", max_length=40)),
                ("identificacion", models.CharField(blank=True, max_length=30)),
                ("activo", models.BooleanField(default=True)),
            ],
            options={"ordering": ("nombre",)},
        ),
        migrations.AddField(
            model_name="cita",
            name="banco",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="citas", to="citas.banco"),
        ),
        migrations.AddField(
            model_name="cita",
            name="comprobante_pago",
            field=models.FileField(blank=True, upload_to="pagos/comprobantes/%Y/%m/"),
        ),
        migrations.AddField(
            model_name="cita",
            name="estado_pago",
            field=models.CharField(choices=[("NO_REQUERIDO", "Pago en clínica"), ("PENDIENTE", "Pendiente de comprobante"), ("EN_REVISION", "En revisión"), ("APROBADO", "Aprobado"), ("RECHAZADO", "Rechazado")], default="NO_REQUERIDO", max_length=20),
        ),
        migrations.AddField(
            model_name="cita",
            name="observacion_pago",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name="cita",
            name="pago_revisado_en",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="cita",
            name="pago_revisado_por",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="pagos_revisados", to=settings.AUTH_USER_MODEL),
        ),
    ]

