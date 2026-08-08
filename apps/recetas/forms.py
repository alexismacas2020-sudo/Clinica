from django import forms

from .models import Receta


class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ("diagnostico", "medicamentos", "dosis", "frecuencia", "duracion", "indicaciones", "observaciones")
        widgets = {
            "diagnostico": forms.Textarea(attrs={"rows": 3}),
            "medicamentos": forms.Textarea(attrs={"rows": 4, "placeholder": "Un medicamento por línea"}),
            "dosis": forms.Textarea(attrs={"rows": 2}),
            "frecuencia": forms.Textarea(attrs={"rows": 2}),
            "indicaciones": forms.Textarea(attrs={"rows": 3}),
            "observaciones": forms.Textarea(attrs={"rows": 2}),
        }
