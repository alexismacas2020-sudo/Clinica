from django.urls import path

from . import views

app_name = "medicos"

urlpatterns = [
    path("", views.lista, name="lista"),
]
