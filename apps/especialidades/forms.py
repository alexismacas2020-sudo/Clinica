from django import forms

from .models import Especialidad


class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ("nombre", "descripcion", "imagen", "activo")
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}
