from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0002_perfil_recepcionista_y_fechas")]
    operations = [
        migrations.AddField(model_name="perfil", name="activo", field=models.BooleanField(default=True)),
        migrations.AddField(model_name="perfil", name="creado_en", field=models.DateTimeField(auto_now_add=True, default=timezone.now), preserve_default=False),
        migrations.AddField(model_name="perfil", name="actualizado_en", field=models.DateTimeField(auto_now=True, default=timezone.now), preserve_default=False),
    ]
