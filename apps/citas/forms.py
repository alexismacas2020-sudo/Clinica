from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico
from apps.usuarios.models import Perfil

from .models import Banco, Cita


class AgendarCitaForm(forms.ModelForm):
    acepta_terminos = forms.BooleanField(
        required=True,
        label="Acepto los Términos y Condiciones de Agendamiento",
        error_messages={"required": "Debes aceptar los términos y condiciones para solicitar la cita."},
        widget=forms.CheckboxInput(attrs={"data-terms-checkbox": "", "required": True}),
    )

    class Meta:
        model = Cita
        fields = ("especialidad", "medico", "fecha", "hora", "motivo", "metodo_pago", "banco", "comprobante_pago")
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
        self.fields["banco"].queryset = Banco.objects.filter(activo=True)
        self.fields["banco"].empty_label = "Selecciona el banco de destino"
        self.fields["comprobante_pago"].required = False
        self.fields["comprobante_pago"].help_text = "Para transferencia puedes subir el comprobante ahora o después."

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
        metodo = cleaned_data.get("metodo_pago") or Cita.TRANSFERENCIA
        cleaned_data["metodo_pago"] = metodo
        if metodo == Cita.TRANSFERENCIA and not cleaned_data.get("banco"):
            self.add_error("banco", "Selecciona la cuenta bancaria a la que realizaste la transferencia.")
        return cleaned_data

    def save(self, commit=True):
        cita = super().save(commit=False)
        pago_cambio = not cita.pk or any(campo in self.changed_data for campo in ("metodo_pago", "banco", "comprobante_pago"))
        if pago_cambio:
            if cita.metodo_pago == Cita.TRANSFERENCIA:
                cita.estado_pago = Cita.EN_REVISION if cita.comprobante_pago else Cita.PAGO_PENDIENTE
            else:
                cita.banco = None
                cita.comprobante_pago = ""
                cita.estado_pago = Cita.PAGO_PENDIENTE
                cita.observacion_pago = ""
        if commit:
            cita.save()
            self.save_m2m()
        return cita


class CitaRecepcionForm(AgendarCitaForm):
    paciente = forms.ModelChoiceField(queryset=get_user_model().objects.none())
    pago_efectivo_recibido = forms.BooleanField(
        required=False,
        label="El pago en efectivo ya fue recibido",
        help_text="Déjalo sin marcar para confirmar la cita con el pago pendiente.",
    )

    class Meta(AgendarCitaForm.Meta):
        fields = ("paciente", "especialidad", "medico", "fecha", "hora", "motivo", "metodo_pago", "banco", "comprobante_pago")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El personal confirma estas condiciones directamente con el paciente.
        self.fields.pop("acepta_terminos", None)
        self.fields["metodo_pago"].required = False
        self.fields["metodo_pago"].initial = Cita.EFECTIVO
        self.fields["paciente"].queryset = get_user_model().objects.filter(
            perfil__rol=Perfil.Rol.PACIENTE,
            perfil__activo=True,
            is_active=True,
        ).order_by("first_name", "last_name", "username")
        self.fields["paciente"].empty_label = "Selecciona un paciente"
        self.fields["paciente"].label_from_instance = lambda usuario: (
            f"{usuario.get_full_name() or usuario.username} · {usuario.email or 'sin correo'}"
        )

    def clean(self):
        cleaned_data = super().clean()
        if not self.data.get("metodo_pago"):
            cleaned_data["metodo_pago"] = Cita.EFECTIVO
            self.instance.metodo_pago = Cita.EFECTIVO
        # Recepción puede registrar la cita y dejar que el paciente elija
        # posteriormente la cuenta al enviar su comprobante.
        if not cleaned_data.get("banco"):
            self._errors.pop("banco", None)
        return cleaned_data

    def save(self, commit=True):
        cita = super().save(commit=False)
        if cita.metodo_pago == Cita.EFECTIVO:
            cita.estado_pago = Cita.APROBADO if self.cleaned_data.get("pago_efectivo_recibido") else Cita.PAGO_PENDIENTE
            cita.observacion_pago = "Pago en efectivo recibido en recepción." if cita.estado_pago == Cita.APROBADO else ""
        if commit:
            cita.save()
            self.save_m2m()
        return cita


class ComprobantePagoForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ("banco", "comprobante_pago")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["banco"].queryset = Banco.objects.filter(activo=True)
        self.fields["comprobante_pago"].required = True

    def clean_comprobante_pago(self):
        archivo = self.cleaned_data["comprobante_pago"]
        if archivo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("El comprobante no puede superar 5 MB.")
        extensiones = (".pdf", ".jpg", ".jpeg", ".png", ".webp")
        if not archivo.name.lower().endswith(extensiones):
            raise forms.ValidationError("Sube un archivo PDF, JPG, PNG o WEBP.")
        return archivo


class RevisarPagoForm(forms.Form):
    decision = forms.ChoiceField(choices=((Cita.APROBADO, "Aprobar"), (Cita.RECHAZADO, "Rechazar")))
    observacion = forms.CharField(required=False, max_length=240, widget=forms.Textarea(attrs={"rows": 3}))

    def clean(self):
        datos = super().clean()
        if datos.get("decision") == Cita.RECHAZADO and not datos.get("observacion", "").strip():
            self.add_error("observacion", "Indica el motivo del rechazo.")
        return datos


class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = (
            "nombre", "titular", "numero_cuenta", "tipo_cuenta", "identificacion",
            "codigo_qr", "codigo_qr_url", "activo",
        )
