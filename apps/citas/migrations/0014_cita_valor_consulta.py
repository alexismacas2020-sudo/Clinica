from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("citas", "0013_cambiar_sms_a_email")]
    operations = [migrations.AddField(model_name="cita", name="valor_consulta", field=models.DecimalField(decimal_places=2, default=Decimal("30.00"), max_digits=8))]
