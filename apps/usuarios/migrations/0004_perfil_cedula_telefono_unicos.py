from django.db import migrations, models


def limpiar_vacios(apps, schema_editor):
    Perfil = apps.get_model("usuarios", "Perfil")
    Perfil.objects.filter(telefono="").update(telefono=None)


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0003_perfil_activo_fechas")]
    operations = [
        migrations.AlterField(model_name="perfil", name="telefono", field=models.CharField(blank=True, max_length=20, null=True, verbose_name="Número de WhatsApp")),
        migrations.RunPython(limpiar_vacios, migrations.RunPython.noop),
        migrations.AddField(model_name="perfil", name="cedula", field=models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name="Cédula")),
        migrations.AlterField(model_name="perfil", name="telefono", field=models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name="Número de WhatsApp")),
    ]
