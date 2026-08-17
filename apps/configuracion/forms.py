from django import forms

from .models import ConfiguracionEmergencia


class ConfiguracionEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionEmergencia
        fields = ["titulo", "mensaje", "telefono", "whatsapp", "activo"]
        widgets = {
            "mensaje": forms.Textarea(attrs={"rows": 3}),
        }

