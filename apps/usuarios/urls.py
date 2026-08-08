from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "usuarios"

urlpatterns = [

    path(
        "login/",
        views.LoginUsuarioView.as_view(),
        name="login"
    ),


    path("logout/", views.LogoutUsuarioView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),
    path("perfil/", views.perfil, name="perfil"),
    path("panel/", views.panel, name="panel"),
    path("administracion/medicos/nuevo/", views.crear_medico, name="crear_medico"),
    path("administracion/recepcionistas/nuevo/", views.crear_recepcionista, name="crear_recepcionista"),
    path("administracion/usuarios/", views.admin_usuarios, name="admin_usuarios"),
    path("administracion/usuarios/<int:pk>/", views.admin_usuario_detalle, name="admin_usuario_detalle"),
    path("administracion/usuarios/<int:pk>/editar/", views.admin_usuario_editar, name="admin_usuario_editar"),
    path("administracion/usuarios/<int:pk>/estado/", views.admin_usuario_estado, name="admin_usuario_estado"),
    path("administracion/usuarios/<int:pk>/password/", views.admin_usuario_password, name="admin_usuario_password"),
    path("recuperar-contrasena/", views.RecuperarContrasenaView.as_view(), name="password_reset"),
    path("recuperar-contrasena/hecho/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("restablecer/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("restablecer/hecho/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

]
