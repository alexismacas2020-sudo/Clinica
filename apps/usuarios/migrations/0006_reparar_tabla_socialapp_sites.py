from django.db import migrations


def crear_tabla_intermedia_si_falta(apps, schema_editor):
    SocialApp = apps.get_model("socialaccount", "SocialApp")
    through = SocialApp._meta.get_field("sites").remote_field.through
    tablas = schema_editor.connection.introspection.table_names()
    if through._meta.db_table not in tablas:
        schema_editor.create_model(through)


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0005_codigo_recuperacion_y_telefono_sms"),
        ("socialaccount", "0006_alter_socialaccount_extra_data"),
        ("sites", "0002_alter_domain_unique"),
    ]
    operations = [migrations.RunPython(crear_tabla_intermedia_si_falta, migrations.RunPython.noop)]
