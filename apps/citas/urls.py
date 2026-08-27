from django.urls import path

from . import views

app_name = "citas"

urlpatterns = [
    path("administracion/prueba-email/", views.prueba_email, name="prueba_email"),
    path("agendar/", views.agendar, name="agendar"),
    path("mis-citas/", views.mis_citas, name="mis_citas"),
    path("disponibilidad/calendario/", views.calendario_disponibilidad, name="calendario_disponibilidad"),
    path("disponibilidad/medicos/", views.medicos_por_especialidad, name="medicos_por_especialidad"),
    path("recepcion/nueva/", views.recepcion_crear, name="recepcion_crear"),
    path("recepcion/disponibilidad/", views.verificar_disponibilidad, name="verificar_disponibilidad"),
    path("recepcion/<int:pk>/estado/<str:estado>/", views.cambiar_estado, name="cambiar_estado"),
    path("<int:pk>/comprobante/", views.subir_comprobante, name="subir_comprobante"),
    path("recepcion/<int:pk>/pago/", views.revisar_pago, name="revisar_pago"),
    path("recepcion/<int:pk>/pago-efectivo/", views.registrar_pago_efectivo, name="registrar_pago_efectivo"),
    path("administracion/bancos/", views.administrar_bancos, name="administrar_bancos"),
    path("administracion/bancos/<int:pk>/editar/", views.editar_banco, name="editar_banco"),
    path("administracion/bancos/<int:pk>/eliminar/", views.eliminar_banco, name="eliminar_banco"),
]
