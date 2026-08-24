from django.conf import settings
from django.db import migrations


def normalizar_google_oauth(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    SocialApp = apps.get_model("socialaccount", "SocialApp")

    site, _ = Site.objects.update_or_create(
        pk=settings.SITE_ID,
        defaults={"domain": "clinica-hhvc.onrender.com", "name": "Clínica Reina del Cisne"},
    )

    client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")
    client_secret = getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "")
    aplicaciones = SocialApp.objects.filter(provider="google").order_by("pk")

    if client_id and client_secret:
        # La configuración por entorno es la fuente única en producción.
        aplicaciones.delete()
        return

    # Si se usa configuración desde la base, conserva solo una y vincúlala al sitio actual.
    principal = aplicaciones.first()
    if principal:
        aplicaciones.exclude(pk=principal.pk).delete()
        principal.sites.set([site])


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0006_reparar_tabla_socialapp_sites")]
    operations = [migrations.RunPython(normalizar_google_oauth, migrations.RunPython.noop)]
