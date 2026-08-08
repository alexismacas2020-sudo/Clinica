from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("historial", "0001_initial")]

    operations = [
        migrations.AlterField(model_name="historialclinico", name="motivo_consulta", field=models.TextField(blank=True, max_length=1000)),
        migrations.AlterField(model_name="historialclinico", name="diagnostico", field=models.TextField(blank=True, max_length=3000)),
        migrations.AlterField(model_name="historialclinico", name="tratamiento", field=models.TextField(blank=True, max_length=3000)),
        migrations.AddField(model_name="historialclinico", name="finalizado", field=models.BooleanField(default=True)),
        migrations.AlterField(model_name="historialclinico", name="finalizado", field=models.BooleanField(default=False)),
    ]
