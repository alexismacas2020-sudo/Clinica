from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from apps.especialidades.models import Especialidad
from apps.medicos.models import Medico

from .models import Perfil
from .validators import normalizar_telefono_ecuador, validar_cedula_ecuatoriana


class InicioSesionForm(AuthenticationForm):
    username = forms.CharField(label="Usuario o correo electrónico", error_messages={"required": "Ingresa tu usuario o correo electrónico."}, widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(label="Contraseña", strip=False, error_messages={"required": "Ingresa tu contraseña."}, widget=forms.PasswordInput(attrs={"data-password-input": ""}))
    recordarme = forms.BooleanField(required=False, label="Recordarme")

    def clean(self):
        identificador = self.cleaned_data.get("username", "").strip()
        password = self.cleaned_data.get("password")
        if not identificador or not password:
            return self.cleaned_data
        usuario = get_user_model().objects.filter(Q(email__iexact=identificador) | Q(username__iexact=identificador)).first()
        if usuario is None:
            raise ValidationError("Usuario o contraseña incorrectos.")
        if not usuario.is_active:
            raise ValidationError("Tu cuenta se encuentra desactivada. Comunícate con la clínica.")
        username = usuario.get_username()
        self.user_cache = authenticate(self.request, username=username, password=password)
        if self.user_cache is None:
            raise ValidationError("Usuario o contraseña incorrectos.")
        self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        try:
            perfil = user.perfil
        except Perfil.DoesNotExist:
            raise ValidationError("No fue posible identificar el rol de tu cuenta.")
        if perfil.rol not in Perfil.Rol.values:
            raise ValidationError("No fue posible identificar el rol de tu cuenta.")
        if not perfil.activo:
            raise ValidationError("Tu cuenta se encuentra desactivada. Comunícate con la clínica.")


class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(label="Nombres", max_length=150)
    last_name = forms.CharField(label="Apellidos", max_length=150)
    email = forms.EmailField(label="Correo electrónico")
    cedula = forms.CharField(label="Cédula", max_length=10)
    telefono = forms.CharField(label="Número de WhatsApp", max_length=20, help_text="Ejemplo: 0987654321 o +593987654321")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("first_name", "last_name", "username", "cedula", "email", "telefono")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if get_user_model().objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nombre de usuario ya está registrado.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo electrónico ya está en uso.")
        return email

    def clean_cedula(self):
        cedula = validar_cedula_ecuatoriana(self.cleaned_data["cedula"])
        if Perfil.objects.filter(cedula=cedula).exists():
            raise ValidationError("La cédula ingresada ya está registrada.")
        return cedula

    def clean_telefono(self):
        telefono = normalizar_telefono_ecuador(self.cleaned_data["telefono"])
        if Perfil.objects.filter(telefono=telefono).exists():
            raise ValidationError("El número de WhatsApp ya está registrado.")
        return telefono

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            perfil, _ = Perfil.objects.get_or_create(usuario=user)
            perfil.rol = Perfil.Rol.PACIENTE
            perfil.cedula = self.cleaned_data["cedula"]
            perfil.telefono = self.cleaned_data["telefono"]
            perfil.save(update_fields=["rol", "cedula", "telefono"])
        return user


class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombres", max_length=150, required=False)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=False)
    email = forms.EmailField(label="Correo electrónico")

    class Meta:
        model = Perfil
        fields = ("telefono", "foto")

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name
        self.fields["email"].initial = user.email

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.exclude(pk=self.user.pk).filter(email__iexact=email).exists():
            raise ValidationError("Este correo ya está en uso.")
        return email

    def clean_telefono(self):
        valor = self.cleaned_data.get("telefono")
        if not valor:
            return None
        telefono = normalizar_telefono_ecuador(valor)
        if Perfil.objects.exclude(pk=self.instance.pk).filter(telefono=telefono).exists():
            raise ValidationError("El número de WhatsApp ya está registrado.")
        return telefono

    def save(self, commit=True):
        perfil = super().save(commit=commit)
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save(update_fields=["first_name", "last_name", "email"])
        return perfil


class CrearMedicoForm(forms.Form):
    nombres = forms.CharField(max_length=100)
    apellidos = forms.CharField(max_length=100)
    email = forms.EmailField(label="Correo electrónico")
    especialidad = forms.ModelChoiceField(queryset=Especialidad.objects.none())
    registro_profesional = forms.CharField(max_length=50)
    consultorio = forms.CharField(max_length=100, required=False)
    password = forms.CharField(label="Contraseña temporal", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["especialidad"].queryset = Especialidad.objects.filter(activo=True).order_by("nombre")
        self.fields["especialidad"].empty_label = "Selecciona una especialidad"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe un usuario con este correo.")
        return email

    def clean_registro_profesional(self):
        registro = self.cleaned_data["registro_profesional"].strip()
        if Medico.objects.filter(registro_profesional__iexact=registro).exists():
            raise ValidationError("Ya existe un médico con este registro profesional.")
        return registro

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    @transaction.atomic
    def save(self):
        datos = self.cleaned_data
        base_username = datos["email"].split("@")[0]
        username = base_username
        suffix = 1
        while get_user_model().objects.filter(username__iexact=username).exists():
            username = f"{base_username}{suffix}"
            suffix += 1
        usuario = get_user_model().objects.create_user(
            username=username, email=datos["email"], first_name=datos["nombres"], last_name=datos["apellidos"], password=datos["password"]
        )
        usuario.perfil.rol = Perfil.Rol.MEDICO
        usuario.perfil.save(update_fields=["rol"])
        return Medico.objects.create(usuario=usuario, especialidad=datos["especialidad"], nombres=datos["nombres"], apellidos=datos["apellidos"], registro_profesional=datos["registro_profesional"], consultorio=datos["consultorio"])


class CrearRecepcionistaForm(forms.Form):
    nombres = forms.CharField(max_length=150)
    apellidos = forms.CharField(max_length=150)
    email = forms.EmailField(label="Correo electrónico")
    telefono = forms.CharField(max_length=20, required=False)
    password = forms.CharField(label="Contraseña temporal", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe un usuario con este correo.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def clean_telefono(self):
        valor = self.cleaned_data.get("telefono")
        if not valor:
            return None
        telefono = normalizar_telefono_ecuador(valor)
        if Perfil.objects.filter(telefono=telefono).exists():
            raise ValidationError("El número de WhatsApp ya está registrado.")
        return telefono

    @transaction.atomic
    def save(self):
        datos = self.cleaned_data
        base_username = datos["email"].split("@")[0]
        username = base_username
        suffix = 1
        while get_user_model().objects.filter(username__iexact=username).exists():
            username = f"{base_username}{suffix}"
            suffix += 1
        usuario = get_user_model().objects.create_user(
            username=username,
            email=datos["email"],
            first_name=datos["nombres"],
            last_name=datos["apellidos"],
            password=datos["password"],
        )
        perfil = usuario.perfil
        perfil.rol = Perfil.Rol.RECEPCIONISTA
        perfil.telefono = datos["telefono"]
        perfil.save(update_fields=["rol", "telefono"])
        return usuario


class CrearCredencialPersonalForm(forms.Form):
    TIPOS = (
        (Perfil.Rol.MEDICO, "Médico"),
        (Perfil.Rol.RECEPCIONISTA, "Recepcionista"),
    )

    rol = forms.ChoiceField(label="Tipo de cuenta", choices=TIPOS)
    nombres = forms.CharField(max_length=150)
    apellidos = forms.CharField(max_length=150)
    email = forms.EmailField(label="Correo electrónico")
    telefono = forms.CharField(max_length=20, required=False)
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.none(), required=False
    )
    registro_profesional = forms.CharField(max_length=50, required=False)
    consultorio = forms.CharField(max_length=100, required=False)
    password = forms.CharField(label="Contraseña temporal", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["especialidad"].queryset = Especialidad.objects.filter(
            activo=True
        ).order_by("nombre")
        self.fields["especialidad"].empty_label = "Selecciona una especialidad"
        self.fields["rol"].widget.attrs["data-role-selector"] = ""
        for nombre in ("especialidad", "registro_profesional", "consultorio"):
            self.fields[nombre].widget.attrs["data-medical-field"] = ""

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe un usuario con este correo.")
        return email

    def clean_telefono(self):
        valor = self.cleaned_data.get("telefono")
        if not valor:
            return None
        telefono = normalizar_telefono_ecuador(valor)
        if Perfil.objects.filter(telefono=telefono).exists():
            raise ValidationError("El número de WhatsApp ya está registrado.")
        return telefono

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def clean_registro_profesional(self):
        registro = self.cleaned_data.get("registro_profesional", "").strip()
        if registro and Medico.objects.filter(registro_profesional__iexact=registro).exists():
            raise ValidationError("Ya existe un médico con este registro profesional.")
        return registro

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("rol") == Perfil.Rol.MEDICO:
            if not cleaned_data.get("especialidad"):
                self.add_error("especialidad", "Selecciona la especialidad del médico.")
            if not cleaned_data.get("registro_profesional"):
                self.add_error("registro_profesional", "Ingresa el registro profesional.")
        return cleaned_data

    @transaction.atomic
    def save(self):
        datos = self.cleaned_data
        base_username = datos["email"].split("@")[0]
        username = base_username
        suffix = 1
        while get_user_model().objects.filter(username__iexact=username).exists():
            username = f"{base_username}{suffix}"
            suffix += 1
        usuario = get_user_model().objects.create_user(
            username=username,
            email=datos["email"],
            first_name=datos["nombres"],
            last_name=datos["apellidos"],
            password=datos["password"],
        )
        perfil = usuario.perfil
        perfil.rol = datos["rol"]
        perfil.telefono = datos["telefono"]
        perfil.save(update_fields=["rol", "telefono"])
        if datos["rol"] == Perfil.Rol.MEDICO:
            Medico.objects.create(
                usuario=usuario,
                especialidad=datos["especialidad"],
                nombres=datos["nombres"],
                apellidos=datos["apellidos"],
                registro_profesional=datos["registro_profesional"],
                consultorio=datos["consultorio"],
            )
        return usuario


class AdminUsuarioForm(forms.Form):
    nombres = forms.CharField(max_length=150)
    apellidos = forms.CharField(max_length=150)
    email = forms.EmailField(label="Correo electrónico")
    telefono = forms.CharField(max_length=20, required=False)
    rol = forms.ChoiceField(choices=Perfil.Rol.choices)
    activo = forms.BooleanField(required=False, label="Usuario activo")
    foto = forms.ImageField(required=False)

    def __init__(self, *args, usuario, administrador, **kwargs):
        self.usuario = usuario
        self.administrador = administrador
        perfil = usuario.perfil
        kwargs.setdefault("initial", {
            "nombres": usuario.first_name,
            "apellidos": usuario.last_name,
            "email": usuario.email,
            "telefono": perfil.telefono,
            "rol": perfil.rol,
            "activo": usuario.is_active and perfil.activo,
        })
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.exclude(pk=self.usuario.pk).filter(email__iexact=email).exists():
            raise ValidationError("Ya existe un usuario con este correo.")
        return email

    def clean_telefono(self):
        valor = self.cleaned_data.get("telefono")
        if not valor:
            return None
        telefono = normalizar_telefono_ecuador(valor)
        if Perfil.objects.exclude(pk=self.usuario.perfil.pk).filter(telefono=telefono).exists():
            raise ValidationError("El número de WhatsApp ya está registrado.")
        return telefono

    def clean(self):
        cleaned = super().clean()
        if self.usuario == self.administrador:
            if cleaned.get("rol") != Perfil.Rol.ADMIN:
                self.add_error("rol", "No puedes quitar tu propio rol ADMIN.")
            if not cleaned.get("activo"):
                self.add_error("activo", "No puedes desactivar tu propia cuenta.")
        return cleaned

    @transaction.atomic
    def save(self):
        datos = self.cleaned_data
        usuario = self.usuario
        usuario.first_name = datos["nombres"]
        usuario.last_name = datos["apellidos"]
        usuario.email = datos["email"]
        usuario.is_active = datos["activo"]
        usuario.save(update_fields=["first_name", "last_name", "email", "is_active"])
        perfil = usuario.perfil
        perfil.telefono = datos["telefono"]
        perfil.rol = datos["rol"]
        perfil.activo = datos["activo"]
        if datos.get("foto"):
            perfil.foto = datos["foto"]
        perfil.save()
        return usuario
