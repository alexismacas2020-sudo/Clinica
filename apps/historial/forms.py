from django import forms


class AtencionMedicaForm(forms.Form):
    motivo_consulta = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}))
    peso = forms.DecimalField(required=False, min_value=1, max_value=500, decimal_places=2)
    talla = forms.DecimalField(required=False, min_value=0.3, max_value=3, decimal_places=2)
    temperatura = forms.DecimalField(required=False, min_value=30, max_value=45, decimal_places=1)
    presion_arterial = forms.CharField(required=False, max_length=20, help_text="Ejemplo: 120/80")
    frecuencia_cardiaca = forms.IntegerField(required=False, min_value=20, max_value=250)
    saturacion_oxigeno = forms.IntegerField(required=False, min_value=50, max_value=100)
    diagnostico = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    tratamiento = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    observaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, permitir_incompleto=False, **kwargs):
        super().__init__(*args, **kwargs)
        if permitir_incompleto:
            for campo in ("motivo_consulta", "diagnostico", "tratamiento"):
                self.fields[campo].required = False
