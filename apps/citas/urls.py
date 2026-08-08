from django.urls import path

from . import views

app_name = "citas"

urlpatterns = [
    path("agendar/", views.agendar, name="agendar"),
    path("mis-citas/", views.mis_citas, name="mis_citas"),
    path("disponibilidad/calendario/", views.calendario_disponibilidad, name="calendario_disponibilidad"),
    path("disponibilidad/medicos/", views.medicos_por_especialidad, name="medicos_por_especialidad"),
    path("recepcion/nueva/", views.recepcion_crear, name="recepcion_crear"),
    path("recepcion/<int:pk>/editar/", views.recepcion_editar, name="recepcion_editar"),
    path("recepcion/disponibilidad/", views.verificar_disponibilidad, name="verificar_disponibilidad"),
    path("recepcion/<int:pk>/estado/<str:estado>/", views.cambiar_estado, name="cambiar_estado"),
]
