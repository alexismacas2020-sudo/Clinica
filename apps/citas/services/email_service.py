from django.conf import settings

from apps.usuarios.services.email_service import enviar_correo


def _datos_cita(cita):
    return (
        f"Fecha: {cita.fecha:%d/%m/%Y}\n"
        f"Hora: {cita.hora:%H:%M}\n"
        f"Médico: {cita.medico}\n"
        f"Especialidad: {cita.especialidad.nombre}\n"
        f"Dirección: {settings.CLINICA_DIRECCION}\n"
        f"Valor de la consulta: ${cita.valor_consulta:.2f}\n"
    )


def enviar_recordatorio(cita):
    nombre = cita.paciente.get_full_name() or cita.paciente.username
    mensaje = f"Hola {nombre}:\n\nTe recordamos tu próxima cita.\n\n{_datos_cita(cita)}\nPor favor llega 15 minutos antes."
    return enviar_correo(cita.paciente.email, "Recordatorio de tu cita", mensaje)


def enviar_confirmacion(cita):
    nombre = cita.paciente.get_full_name() or cita.paciente.username
    mensaje = f"Hola {nombre}:\n\nTu cita fue confirmada.\n\n{_datos_cita(cita)}\nPor favor llega 15 minutos antes."
    return enviar_correo(cita.paciente.email, "Tu cita fue confirmada", mensaje)


def enviar_aviso_nueva_cita_clinica(cita):
    """Avisa a la clínica cuando un paciente registra una nueva cita."""
    nombre = cita.paciente.get_full_name() or cita.paciente.username
    correo = cita.paciente.email or "No registrado"
    telefono = getattr(getattr(cita.paciente, "perfil", None), "telefono", "") or "No registrado"
    mensaje = (
        "Se registró una nueva solicitud de cita.\n\n"
        f"Paciente: {nombre}\n"
        f"Correo: {correo}\n"
        f"Teléfono: {telefono}\n"
        f"Motivo: {cita.motivo}\n"
        f"Método de pago: {cita.get_metodo_pago_display()}\n\n"
        f"{_datos_cita(cita)}\n"
        "Ingresa al panel de recepción para revisarla y confirmarla."
    )
    return enviar_correo(
        settings.CONTACT_RECIPIENT_EMAIL,
        f"Nueva cita por confirmar: {nombre}",
        mensaje,
    )


def enviar_estado(cita, estado_anterior=None):
    nombre = cita.paciente.get_full_name() or cita.paciente.username
    contenido = _datos_cita(cita)
    mensajes = {
        cita.PENDIENTE: ("Solicitud de cita recibida", "Recibimos tu solicitud de cita y está pendiente de confirmación."),
        cita.REAGENDADA: ("Tu cita fue reagendada", "Los datos de tu cita cambiaron y está pendiente de una nueva confirmación."),
        cita.CANCELADA: ("Tu cita fue cancelada", "Tu cita fue cancelada. Si necesitas atención, puedes solicitar una nueva fecha."),
        cita.ATENDIDA: ("Tu consulta fue registrada", "Tu consulta finalizó y el informe clínico está disponible de forma segura en tu portal."),
    }
    if cita.estado == cita.CONFIRMADA:
        return enviar_confirmacion(cita)
    asunto, detalle = mensajes[cita.estado]
    return enviar_correo(cita.paciente.email, asunto, f"Hola {nombre}:\n\n{detalle}\n\n{contenido}\nIngresa a tu portal para consultar la información actualizada.")


def enviar_estado_pago(cita):
    nombre = cita.paciente.get_full_name() or cita.paciente.username
    mensajes = {
        cita.PAGO_PENDIENTE: "Tu cita está registrada, pero todavía falta subir el comprobante de transferencia.",
        cita.EN_REVISION: "Recibimos tu comprobante de transferencia y será revisado por la clínica.",
        cita.APROBADO: "Tu comprobante de pago fue aprobado.",
        cita.RECHAZADO: f"Tu comprobante fue rechazado. Motivo: {cita.observacion_pago or 'Consulta con la clínica.'}",
        cita.NO_REQUERIDO: "El pago se realizará directamente en la clínica.",
    }
    return enviar_correo(
        cita.paciente.email,
        "Actualización del pago de tu cita",
        f"Hola {nombre}:\n\n{mensajes[cita.estado_pago]}\n\n{_datos_cita(cita)}\nConsulta el estado actualizado en tu portal.",
    )
