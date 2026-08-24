from django.urls import path
from . import views

app_name = "historial"
urlpatterns = [path("citas/<int:pk>/atender/", views.atender_cita, name="atender_cita")]
urlpatterns += [
    path("mi-historial/", views.mi_historial, name="mi_historial"),
    path("mi-historial/<int:pk>/", views.mi_historial_detalle, name="mi_historial_detalle"),
    path("mis-historiales/", views.mis_historiales, name="mis_historiales"),
    path("mis-historiales/<int:pk>/", views.detalle_historial, name="detalle_historial"),
    path("archivos/<int:pk>/eliminar/", views.eliminar_archivo, name="eliminar_archivo"),
]
