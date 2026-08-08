from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.usuarios.models import Perfil

from .models import Cita


class AgendarCitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ("especialidad", "medico", "fecha", "hora", "motivo")
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "min": timezone.localdate().isoformat()}),
            "hora": forms.TimeInput(attrs={"type": "time"}),
            "motivo": forms.Textarea(attrs={"rows": 3, "placeholder": "Describe brevemente el motivo de tu consulta."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["especialidad"].queryset = Especialidad.objects.filter(activo=True).order_by("nombre")
        self.fields["especialidad"].empty_label = "Selecciona una especialidad"
        medicos = Medico.objects.filter(activo=True).select_related("especialidad")
        especialidad_id = self.data.get("especialidad") or self.initial.get("especialidad")
        if especialidad_id:
            medicos = medicos.filter(especialidad_id=especialidad_id)
        self.fields["medico"].queryset = medicos
        self.fields["medico"].empty_label = "Selecciona un médico"
        self.fields["medico"].label_from_instance = lambda medico: f"{medico} · {medico.especialidad.nombre}"

    def clean(self):
        cleaned_data = super().clean()
        medico = cleaned_data.get("medico")
        especialidad = cleaned_data.get("especialidad")
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")
        if medico and especialidad and medico.especialidad_id != especialidad.id:
            self.add_error("medico", "Selecciona un médico de la especialidad indicada.")
        conflicto = Cita.objects.filter(medico=medico, fecha=fecha, hora=hora).exclude(estado=Cita.CANCELADA)
        if self.instance.pk:
            conflicto = conflicto.exclude(pk=self.instance.pk)
        if medico and fecha and hora and conflicto.exists():
            self.add_error("hora", "Ese horario ya no está disponible. Elige otro.")
        return cleaned_data


class CitaRecepcionForm(AgendarCitaForm):
    paciente = forms.ModelChoiceField(queryset=get_user_model().objects.none())

    class Meta(AgendarCitaForm.Meta):
        fields = ("paciente", "especialidad", "medico", "fecha", "hora", "motivo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["paciente"].queryset = get_user_model().objects.filter(
            perfil__rol=Perfil.Rol.PACIENTE,
            perfil__activo=True,
            is_active=True,
        ).order_by("first_name", "last_name", "username")
        self.fields["paciente"].empty_label = "Selecciona un paciente"
        self.fields["paciente"].label_from_instance = lambda usuario: (
            f"{usuario.get_full_name() or usuario.username} · {usuario.email or 'sin correo'}"
        )
