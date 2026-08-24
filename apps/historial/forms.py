from django import forms

from .models import ArchivoHistorial


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        archivos = data if isinstance(data, (list, tuple)) else [data]
        limpiar_archivo = super().clean
        return [limpiar_archivo(archivo, initial) for archivo in archivos if archivo]


class AtencionMedicaForm(forms.Form):
    motivo_consulta = forms.CharField(label="Motivo de consulta", widget=forms.Textarea(attrs={"rows": 3}))
    peso = forms.DecimalField(label="Peso (kg)", required=False, min_value=1, max_value=500, decimal_places=2, help_text="Kilogramos. Ejemplo: 68.50 kg")
    talla = forms.DecimalField(label="Talla (m)", required=False, min_value=0.3, max_value=3, decimal_places=2, help_text="Metros. Ejemplo: 1.70 m")
    temperatura = forms.DecimalField(label="Temperatura (°C)", required=False, min_value=30, max_value=45, decimal_places=1, help_text="Grados Celsius. Ejemplo: 36.5 °C")
    presion_arterial = forms.CharField(
        label="Presión arterial",
        required=False,
        max_length=20,
        help_text="Escribe la lectura completa como texto. Ejemplo: 120/80 mmHg.",
        widget=forms.TextInput(attrs={"placeholder": "Ej.: 120/80 mmHg", "inputmode": "text"}),
    )
    frecuencia_cardiaca = forms.IntegerField(label="Frecuencia cardiaca (lpm)", required=False, min_value=20, max_value=250, help_text="Latidos por minuto. Ejemplo: 72 lpm")
    saturacion_oxigeno = forms.IntegerField(label="Saturación de oxígeno (%)", required=False, min_value=50, max_value=100, help_text="Porcentaje SpO₂. Ejemplo: 98%")
    diagnostico = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    tratamiento = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    observaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    tipo_archivo = forms.ChoiceField(
        label="Tipo de archivo clínico", required=False, choices=ArchivoHistorial.TIPOS,
    )
    archivos_clinicos = MultipleFileField(
        label="Seleccionar archivos", required=False,
        help_text="Puedes seleccionar varios archivos. Máximo 10 MB por archivo.",
        widget=MultipleFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png,.webp,.dcm"}),
    )
    descripcion_archivos = forms.CharField(
        label="Descripción", required=False, max_length=250,
        widget=forms.TextInput(attrs={"placeholder": "Ej.: Radiografía de tórax"}),
    )

    def __init__(self, *args, permitir_incompleto=False, **kwargs):
        super().__init__(*args, **kwargs)
        if permitir_incompleto:
            for campo in ("motivo_consulta", "diagnostico", "tratamiento"):
                self.fields[campo].required = False

    def clean_archivos_clinicos(self):
        archivos = self.cleaned_data.get("archivos_clinicos", [])
        permitidas = {"pdf", "jpg", "jpeg", "png", "webp", "dcm"}
        for archivo in archivos:
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError(f"{archivo.name}: el archivo supera 10 MB.")
            extension = archivo.name.rsplit(".", 1)[-1].lower() if "." in archivo.name else ""
            if extension not in permitidas:
                raise forms.ValidationError(f"{archivo.name}: formato no permitido.")
        return archivos


class ArchivoHistorialForm(forms.ModelForm):
    class Meta:
        model = ArchivoHistorial
        fields = ("tipo", "archivo", "descripcion")
        widgets = {"archivo": forms.ClearableFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png,.webp,.dcm"})}

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        if archivo.size > 10 * 1024 * 1024:
            raise forms.ValidationError("El archivo no puede superar 10 MB.")
        extension = archivo.name.rsplit(".", 1)[-1].lower() if "." in archivo.name else ""
        if extension not in {"pdf", "jpg", "jpeg", "png", "webp", "dcm"}:
            raise forms.ValidationError("Formato no permitido. Usa PDF, JPG, PNG, WEBP o DICOM.")
        return archivo
