from django import forms

from apps.especialidades.models import Especialidad

from .models import Medico


class MedicoAdminForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = (
            "nombres", "apellidos", "especialidad", "registro_profesional",
            "foto", "foto_url", "consultorio", "duracion_consulta", "biografia",
            "destacado", "activo",
        )
        widgets = {"biografia": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["especialidad"].queryset = Especialidad.objects.order_by("nombre")
        self.fields["foto"].help_text = "JPG, PNG o WEBP. La imagen se mostrará en la página pública."
        self.fields["foto_url"].help_text = "Opcional: pega el enlace directo de una imagen JPG, PNG o WEBP."
