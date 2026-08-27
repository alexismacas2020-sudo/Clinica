from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal


class Cita(models.Model):
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"
    TRANSFERENCIA = "TRANSFERENCIA"
    SEGURO = "SEGURO"
    METODOS_PAGO = [
        (TRANSFERENCIA, "Transferencia bancaria"),
        (EFECTIVO, "Efectivo en la clínica"),
    ]
    NO_REQUERIDO = "NO_REQUERIDO"
    PAGO_PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    ESTADOS_PAGO = [
        (NO_REQUERIDO, "No requiere pago"),
        (PAGO_PENDIENTE, "Pago pendiente"),
        (EN_REVISION, "En revisión"),
        (APROBADO, "Pago realizado"),
        (RECHAZADO, "Rechazado"),
    ]
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    ATENDIDA = "ATENDIDA"
    REAGENDADA = "REAGENDADA"
    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (CONFIRMADA, "Confirmada"),
        (REAGENDADA, "Reagendada"),
        (ATENDIDA, "Realizada"),
        (CANCELADA, "Cancelada"),
    ]

    paciente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="citas")
    medico = models.ForeignKey("medicos.Medico", on_delete=models.PROTECT, related_name="citas")
    especialidad = models.ForeignKey("especialidades.Especialidad", on_delete=models.PROTECT, related_name="citas")
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField(max_length=500)
    estado = models.CharField(max_length=12, choices=ESTADOS, default=PENDIENTE)
    creado_en = models.DateTimeField(auto_now_add=True)
    recordatorio_email_enviado = models.BooleanField(default=False)
    fecha_recordatorio_email = models.DateTimeField(null=True, blank=True)
    estado_recordatorio_email = models.CharField(max_length=30, blank=True)
    error_recordatorio_email = models.TextField(blank=True)
    confirmacion_email_enviada = models.BooleanField(default=False)
    fecha_confirmacion_email = models.DateTimeField(null=True, blank=True)
    error_confirmacion_email = models.TextField(blank=True)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default=TRANSFERENCIA)
    banco = models.ForeignKey("Banco", on_delete=models.PROTECT, related_name="citas", null=True, blank=True)
    comprobante_pago = models.FileField(upload_to="pagos/comprobantes/%Y/%m/", blank=True)
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default=NO_REQUERIDO)
    observacion_pago = models.CharField(max_length=240, blank=True)
    pago_revisado_en = models.DateTimeField(null=True, blank=True)
    pago_revisado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="pagos_revisados", null=True, blank=True)
    valor_consulta = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("30.00"))

    class Meta:
        ordering = ("fecha", "hora")
        constraints = [
            models.UniqueConstraint(
                fields=("medico", "fecha", "hora"),
                condition=~models.Q(estado="CANCELADA"),
                name="cita_medico_fecha_hora_activa_unica",
            )
        ]

    def clean(self):
        if self.fecha and self.fecha < date.today():
            raise ValidationError({"fecha": "No puedes agendar una cita en una fecha pasada."})
        if self.medico_id and self.especialidad_id and self.medico.especialidad_id != self.especialidad_id:
            raise ValidationError({"medico": "El médico seleccionado no pertenece a esta especialidad."})

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.medico}"

    @property
    def pago_realizado(self):
        return self.estado_pago == self.APROBADO

class Banco(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    titular = models.CharField(max_length=140)
    numero_cuenta = models.CharField(max_length=50)
    tipo_cuenta = models.CharField(max_length=40, default="Cuenta corriente")
    identificacion = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)
    codigo_qr = models.ImageField(upload_to="pagos/codigos_qr/", blank=True, verbose_name="Código QR de pago")

    class Meta:
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre
