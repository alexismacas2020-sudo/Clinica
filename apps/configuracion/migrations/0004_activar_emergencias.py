from django.db import migrations


def activar_emergencias(apps, schema_editor):
    Configuracion = apps.get_model("configuracion", "ConfiguracionEmergencia")
    configuracion = Configuracion.objects.order_by("pk").first()
    if configuracion is None:
        Configuracion.objects.create(
            titulo="¿Tienes una emergencia?",
            mensaje="Si hay riesgo vital, llama ahora. Nuestro equipo está disponible para orientarte.",
            telefono="0988128636",
            activo=True,
        )
    else:
        configuracion.telefono = "0988128636"
        configuracion.activo = True
        configuracion.save(update_fields=["telefono", "activo"])


class Migration(migrations.Migration):
    dependencies = [("configuracion", "0003_telefono_emergencias")]
    operations = [migrations.RunPython(activar_emergencias, migrations.RunPython.noop)]
