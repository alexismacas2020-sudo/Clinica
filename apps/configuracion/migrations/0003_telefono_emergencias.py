from django.db import migrations, models


def actualizar_telefono(apps, schema_editor):
    Configuracion = apps.get_model("configuracion", "ConfiguracionEmergencia")
    Configuracion.objects.filter(telefono__in=["", "911"]).update(telefono="0988128636")


class Migration(migrations.Migration):
    dependencies = [("configuracion", "0002_configuracion_pagina_principal")]
    operations = [
        migrations.AlterField(model_name="configuracionemergencia", name="telefono", field=models.CharField(default="0988128636", max_length=30)),
        migrations.RunPython(actualizar_telefono, migrations.RunPython.noop),
    ]
