from django.urls import path

from . import views

app_name = "especialidades"

urlpatterns = [
    path("administrar/", views.administrar, name="administrar"),
    path("administrar/<int:pk>/editar/", views.editar, name="editar"),
    path("administrar/<int:pk>/activar/", views.cambiar_activo, name="cambiar_activo"),
    path("administrar/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
