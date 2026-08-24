from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from datetime import timedelta
import secrets

from apps.citas.models import Cita
from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico

from .decorators import solo_administrador, usuario_con_perfil_activo
from .forms import AdminUsuarioForm, CrearMedicoForm, CrearRecepcionistaForm, InicioSesionForm, PerfilForm, RegistroUsuarioForm, SolicitarCodigoForm, VerificarCodigoForm
from .models import CodigoRecuperacion, Perfil
from .services.email_service import EmailError, enviar_correo


def destino_por_rol(usuario):
    perfil, _ = Perfil.objects.get_or_create(usuario=usuario, defaults={"rol": Perfil.Rol.ADMIN if usuario.is_superuser else Perfil.Rol.PACIENTE})
    if usuario.is_superuser:
        return reverse("dashboard:admin")
    destinos = {Perfil.Rol.ADMIN: "dashboard:admin", Perfil.Rol.RECEPCIONISTA: "dashboard:recepcionista", Perfil.Rol.MEDICO: "dashboard:medico", Perfil.Rol.PACIENTE: "dashboard:paciente"}
    return reverse(destinos[perfil.rol])


class LoginUsuarioView(LoginView):
    template_name = "usuarios/auth/login.html"
    authentication_form = InicioSesionForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or destino_por_rol(self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get("recordarme"):
            self.request.session.set_expiry(0)
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Corrige los errores del formulario para continuar.")
        return super().form_invalid(form)


class LogoutUsuarioView(LogoutView):
    next_page = reverse_lazy("pagina:inicio")


def recuperar_contrasena(request):
    form = SolicitarCodigoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].strip().lower()
        perfil = Perfil.objects.select_related("usuario").filter(usuario__email__iexact=email, activo=True, usuario__is_active=True).first()
        if perfil:
            reciente = CodigoRecuperacion.objects.filter(usuario=perfil.usuario, creado_en__gte=timezone.now() - timedelta(seconds=60)).exists()
            if reciente:
                form.add_error(None, "Espera un minuto antes de solicitar otro código.")
                return render(request, "usuarios/password_reset.html", {"form": form})
            codigo = f"{secrets.randbelow(1_000_000):06d}"
            registro = CodigoRecuperacion.objects.create(usuario=perfil.usuario, codigo_hash=make_password(codigo), expira_en=timezone.now() + timedelta(minutes=10))
            try:
                enviar_correo(email, "Código para cambiar tu contraseña", f"Tu código de recuperación es {codigo}.\n\nVence en 10 minutos. Si no solicitaste este cambio, ignora este correo.")
            except EmailError as exc:
                registro.delete()
                form.add_error(None, str(exc))
                return render(request, "usuarios/password_reset.html", {"form": form})
            request.session["recuperacion_codigo_id"] = registro.pk
        messages.success(request, "Si el correo está registrado, recibirás un código de recuperación.")
        return redirect("usuarios:password_reset_verify")
    return render(request, "usuarios/password_reset.html", {"form": form})


def verificar_codigo(request):
    registro = CodigoRecuperacion.objects.select_related("usuario").filter(pk=request.session.get("recuperacion_codigo_id")).first()
    if not registro:
        messages.error(request, "Solicita un nuevo código para continuar.")
        return redirect("usuarios:password_reset")
    form = VerificarCodigoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not registro.vigente:
            form.add_error(None, "El código venció o alcanzó el límite de intentos.")
        elif check_password(form.cleaned_data["codigo"], registro.codigo_hash):
            request.session["recuperacion_usuario_id"] = registro.usuario_id
            request.session["recuperacion_verificada"] = True
            return redirect("usuarios:password_reset_change")
        else:
            registro.intentos += 1
            registro.save(update_fields=["intentos"])
            form.add_error("codigo", "El código es incorrecto.")
    return render(request, "usuarios/password_reset_verify.html", {"form": form})


def cambiar_contrasena_email(request):
    usuario_id = request.session.get("recuperacion_usuario_id")
    if not request.session.get("recuperacion_verificada") or not usuario_id:
        return redirect("usuarios:password_reset")
    usuario = get_object_or_404(get_user_model(), pk=usuario_id, is_active=True)
    form = SetPasswordForm(usuario, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        CodigoRecuperacion.objects.filter(pk=request.session.get("recuperacion_codigo_id")).update(usado_en=timezone.now())
        for clave in ("recuperacion_codigo_id", "recuperacion_usuario_id", "recuperacion_verificada"):
            request.session.pop(clave, None)
        messages.success(request, "Tu contraseña fue cambiada. Ya puedes iniciar sesión.")
        return redirect("usuarios:login")
    return render(request, "usuarios/password_reset_change.html", {"form": form})


def registro(request):
    if request.user.is_authenticated:
        return redirect(destino_por_rol(request.user))
    form = RegistroUsuarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tu cuenta fue creada correctamente. Ahora inicia sesión con tus credenciales.")
        return redirect("usuarios:login")
    if request.method == "POST":
        messages.error(request, "Corrige los errores del formulario para continuar.")
    return render(request, "usuarios/auth/registro.html", {"form": form})


@usuario_con_perfil_activo
def perfil(request):
    perfil_usuario = request.user.perfil
    form = PerfilForm(request.POST or None, request.FILES or None, instance=perfil_usuario, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tu perfil fue actualizado.")
        return redirect("usuarios:perfil")
    return render(request, "usuarios/perfil.html", {"form": form, "perfil": perfil_usuario})


@usuario_con_perfil_activo
def panel(request):
    perfil_usuario = request.user.perfil

    # Los paneles operativos conservan su dashboard específico por rol.
    if request.user.is_superuser or perfil_usuario.rol != Perfil.Rol.PACIENTE:
        return redirect(destino_por_rol(request.user))

    hoy = timezone.localdate()
    citas = Cita.objects.filter(paciente=request.user).select_related(
        "medico", "especialidad"
    )
    contexto = {
        "perfil": perfil_usuario,
        "rol": perfil_usuario.rol,
        "titulo_panel": "Mi panel de salud",
        "proxima_cita": citas.filter(fecha__gte=hoy)
        .exclude(estado=Cita.CANCELADA)
        .first(),
        "citas_recientes": citas.order_by("-fecha", "-hora")[:4],
        "especialidades_destacadas": Especialidad.objects.filter(activo=True)[:5],
        "medicos_destacados": Medico.objects.filter(activo=True)
        .select_related("especialidad")
        .order_by("-destacado", "nombres")[:3],
    }
    return render(request, "usuarios/panel.html", contexto)


@solo_administrador
def crear_medico(request):
    form = CrearMedicoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        medico = form.save()
        messages.success(request, f"Se crearon las credenciales de {medico}.")
        return redirect("usuarios:crear_medico")
    if request.method == "POST":
        messages.error(request, "No se pudo crear el médico. Revisa los campos señalados.")
    return render(request, "usuarios/crear_medico.html", {"form": form})


@solo_administrador
def crear_recepcionista(request):
    form = CrearRecepcionistaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(request, f"Se crearon las credenciales de recepción para {usuario.get_full_name()}.")
        return redirect("usuarios:crear_recepcionista")
    if request.method == "POST":
        messages.error(request, "No se pudo crear la credencial de recepción. Revisa los campos señalados.")
    return render(request, "usuarios/crear_recepcionista.html", {"form": form})


@solo_administrador
def admin_usuarios(request):
    usuarios = get_user_model().objects.select_related("perfil").order_by("first_name", "last_name", "username")
    busqueda = request.GET.get("q", "").strip()
    rol = request.GET.get("rol", "").strip()
    estado = request.GET.get("estado", "").strip()
    if busqueda:
        usuarios = usuarios.filter(
            Q(first_name__icontains=busqueda) | Q(last_name__icontains=busqueda)
            | Q(username__icontains=busqueda) | Q(email__icontains=busqueda)
        )
    if rol in Perfil.Rol.values:
        usuarios = usuarios.filter(perfil__rol=rol)
    if estado == "activo":
        usuarios = usuarios.filter(is_active=True, perfil__activo=True)
    elif estado == "inactivo":
        usuarios = usuarios.filter(Q(is_active=False) | Q(perfil__activo=False))
    pagina = Paginator(usuarios, 12).get_page(request.GET.get("page"))
    return render(request, "usuarios/admin_lista.html", {
        "pagina": pagina, "busqueda": busqueda, "rol_actual": rol,
        "estado_actual": estado, "roles": Perfil.Rol.choices,
    })


@solo_administrador
def admin_usuario_detalle(request, pk):
    usuario = get_object_or_404(get_user_model().objects.select_related("perfil"), pk=pk)
    if usuario.perfil.rol == Perfil.Rol.MEDICO and hasattr(usuario, "medico"):
        citas = Cita.objects.filter(medico=usuario.medico)
    else:
        citas = Cita.objects.filter(paciente=usuario)
    citas = citas.select_related("paciente", "medico", "especialidad").order_by("-fecha", "-hora")[:8]
    return render(request, "usuarios/admin_detalle.html", {"usuario_perfil": usuario, "citas_usuario": citas})


@solo_administrador
def admin_usuario_editar(request, pk):
    usuario = get_object_or_404(get_user_model().objects.select_related("perfil"), pk=pk)
    form = AdminUsuarioForm(request.POST or None, request.FILES or None, usuario=usuario, administrador=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "El perfil del usuario fue actualizado.")
        return redirect("usuarios:admin_usuario_detalle", pk=usuario.pk)
    return render(request, "usuarios/admin_editar.html", {"form": form, "usuario_perfil": usuario})


@solo_administrador
def admin_usuario_estado(request, pk):
    usuario = get_object_or_404(get_user_model().objects.select_related("perfil"), pk=pk)
    if request.method == "POST":
        if usuario == request.user:
            messages.error(request, "No puedes desactivar tu propia cuenta.")
        else:
            nuevo_estado = not (usuario.is_active and usuario.perfil.activo)
            usuario.is_active = nuevo_estado
            usuario.save(update_fields=["is_active"])
            usuario.perfil.activo = nuevo_estado
            usuario.perfil.save(update_fields=["activo"])
            messages.success(request, "Usuario activado." if nuevo_estado else "Usuario desactivado.")
    return redirect("usuarios:admin_usuario_detalle", pk=usuario.pk)


@solo_administrador
def admin_usuario_password(request, pk):
    usuario = get_object_or_404(get_user_model().objects.select_related("perfil"), pk=pk)
    form = SetPasswordForm(usuario, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"La contraseña de {usuario.username} fue actualizada.")
        return redirect("usuarios:admin_usuario_detalle", pk=usuario.pk)
    return render(request, "usuarios/admin_password.html", {"form": form, "usuario_perfil": usuario})
