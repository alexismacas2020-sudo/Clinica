from django.urls import path
from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.dashboard_admin, name="admin"),
    path("admin/", views.dashboard_admin, name="admin_legacy"),
    path("credenciales/nueva/", views.crear_credencial, name="crear_credencial"),
    path("recepcion/", views.dashboard_recepcionista, name="recepcionista"),
    path("medico/", views.dashboard_medico, name="medico"),
    path("paciente/", views.dashboard_paciente, name="paciente"),
]
