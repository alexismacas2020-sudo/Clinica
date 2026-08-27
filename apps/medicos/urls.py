from django.urls import path

from . import views

app_name = "medicos"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("administrar/", views.administrar, name="administrar"),
    path("administrar/<int:pk>/editar/", views.editar, name="editar"),
    path("administrar/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
