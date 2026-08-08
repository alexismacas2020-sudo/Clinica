from django.urls import path
from . import views

app_name = "recetas"
urlpatterns = [
    path("historial/<int:historial_pk>/emitir/", views.emitir, name="emitir"),
    path("mis-recetas/", views.mis_recetas, name="mis_recetas"),
    path("<int:pk>/descargar/", views.descargar, name="descargar"),
    path("verificar/<uuid:codigo>/", views.verificar, name="verificar"),
]
