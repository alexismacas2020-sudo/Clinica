import apps.historial.models
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("historial", "0002_borradores_atencion"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentoClinico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("archivo", models.FileField(upload_to="historial/documentos/%Y/%m/", validators=[django.core.validators.FileExtensionValidator(["pdf", "png", "jpg", "jpeg", "webp", "dcm", "doc", "docx", "xls", "xlsx", "txt"]), apps.historial.models.validar_tamano_documento])),
                ("descripcion", models.CharField(blank=True, max_length=180)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("historial", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documentos", to="historial.historialclinico")),
                ("subido_por", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="documentos_clinicos_subidos", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-creado_en",)},
        ),
    ]
