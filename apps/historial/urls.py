from django.urls import path
from . import views

app_name = "historial"
urlpatterns = [path("citas/<int:pk>/atender/", views.atender_cita, name="atender_cita")]
urlpatterns += [
    path("mis-historiales/", views.mis_historiales, name="mis_historiales"),
    path("mis-historiales/<int:pk>/", views.detalle_historial, name="detalle_historial"),
]
