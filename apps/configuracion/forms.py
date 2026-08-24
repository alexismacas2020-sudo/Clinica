from django import forms

from .models import ConfiguracionContacto, ConfiguracionEmergencia


class ConfiguracionEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionEmergencia
        fields = ["titulo", "mensaje", "telefono", "activo"]
        widgets = {
            "mensaje": forms.Textarea(attrs={"rows": 3}),
        }


class ConfiguracionContactoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionContacto
        fields = (
            "titulo", "descripcion", "telefono", "correo", "ubicacion", "horario", "enlace_mapa",
            "facebook", "instagram", "whatsapp", "tiktok", "youtube", "linkedin", "activo",
        )
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}

