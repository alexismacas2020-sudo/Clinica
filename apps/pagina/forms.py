from django import forms


class ContactoForm(forms.Form):
    ASUNTOS = (
        ("Información sobre especialidades", "Información sobre especialidades"),
        ("Información sobre citas", "Información sobre citas"),
        ("Servicios médicos", "Servicios médicos"),
        ("Otro", "Otro"),
    )

    nombre = forms.CharField(max_length=120)
    correo = forms.EmailField()
    asunto = forms.ChoiceField(choices=ASUNTOS)
    mensaje = forms.CharField(max_length=2000, widget=forms.Textarea)
