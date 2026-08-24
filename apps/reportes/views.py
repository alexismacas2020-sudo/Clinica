from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone
from datetime import date

from apps.citas.models import Cita
from apps.historial.models import HistorialClinico
from apps.usuarios.decorators import administrador_o_recepcionista
from apps.usuarios.models import Perfil


@administrador_o_recepcionista
def resumen(request):
    hoy = timezone.localdate()
    desde = request.GET.get("desde") or hoy.replace(day=1).isoformat()
    hasta = request.GET.get("hasta") or hoy.isoformat()
    try:
        date.fromisoformat(desde)
        date.fromisoformat(hasta)
    except ValueError:
        desde, hasta = hoy.replace(day=1).isoformat(), hoy.isoformat()
    citas = Cita.objects.filter(fecha__range=(desde, hasta)).select_related("paciente", "medico", "especialidad", "banco")
    total_citas = citas.count()
    por_estado = {item["estado"]: item["total"] for item in citas.values("estado").annotate(total=Count("id"))}
    por_especialidad = list(
        citas.values("especialidad__nombre")
        .annotate(
            total_citas=Count("id"),
            total_atendidas=Count("id", filter=models.Q(estado=Cita.ATENDIDA)),
            facturacion=Sum("valor_consulta", filter=models.Q(estado_pago=Cita.APROBADO)),
        )
        .order_by("-facturacion", "especialidad__nombre")
    )
    por_medico = list(
        citas.values("medico_id", "medico__nombres", "medico__apellidos", "medico__especialidad__nombre")
        .annotate(total_citas=Count("id"), facturacion=Sum("valor_consulta", filter=models.Q(estado_pago=Cita.APROBADO)))
        .order_by("-facturacion", "medico__apellidos", "medico__nombres")
    )
    enfermedades = list(
        HistorialClinico.objects.filter(finalizado=True, cita__fecha__range=(desde, hasta))
        .exclude(diagnostico__exact="")
        .values("diagnostico")
        .annotate(total=Count("id"))
        .order_by("-total", "diagnostico")[:20]
    )
    contexto = {
        "desde": desde, "hasta": hasta, "citas": citas.order_by("-fecha", "-hora")[:100],
        "total_citas": total_citas, "confirmadas": por_estado.get(Cita.CONFIRMADA, 0),
        "atendidas": por_estado.get(Cita.ATENDIDA, 0), "canceladas": por_estado.get(Cita.CANCELADA, 0),
        "pagos_revision": citas.filter(estado_pago=Cita.EN_REVISION).count(),
        "ingresos_aprobados": citas.filter(estado_pago=Cita.APROBADO).aggregate(total=Sum("valor_consulta"))["total"] or 0,
        "total_pacientes": get_user_model().objects.filter(perfil__rol=Perfil.Rol.PACIENTE, is_active=True).count(),
        "porcentaje_atendidas": round(por_estado.get(Cita.ATENDIDA, 0) * 100 / total_citas) if total_citas else 0,
        "por_especialidad": por_especialidad,
        "por_medico": por_medico,
        "medico_mayor_facturacion": por_medico[0] if por_medico and (por_medico[0]["facturacion"] or 0) > 0 else None,
        "enfermedades": enfermedades,
    }
    return render(request, "reportes/resumen.html", contexto)
