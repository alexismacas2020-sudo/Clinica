from pathlib import Path
import environ


# =====================================================
# DIRECTORIOS DEL PROYECTO
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# =====================================================
# VARIABLES DE ENTORNO
# =====================================================

env = environ.Env(
    DEBUG=(bool, True)
)

env.read_env(
    BASE_DIR / ".env"
)


# =====================================================
# SEGURIDAD
# =====================================================

SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-change-this"
)

DEBUG = env(
    "DEBUG",
    default=True
)

ALLOWED_HOSTS = []


# =====================================================
# APLICACIONES INSTALADAS
# =====================================================

INSTALLED_APPS = [

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",


    # Librerías externas
    "rest_framework",

    "crispy_forms",
    "crispy_bootstrap5",
    "cloudinary",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",


    # Aplicaciones del sistema clínico

   

    "apps.pagina",

    "apps.especialidades",

    "apps.medicos",

    "apps.pacientes",

    "apps.usuarios",

    "apps.citas",

    "apps.horarios",

    "apps.historial",

    "apps.recetas",

    "apps.reportes",

    "apps.dashboard",

    "apps.notificaciones",

    "apps.auditoria",

    "apps.configuracion",

    "apps.api",

]

# =====================================================
# MIDDLEWARE
# =====================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "allauth.account.middleware.AccountMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]


# =====================================================
# URLS
# =====================================================

ROOT_URLCONF = "config.urls"


# =====================================================
# TEMPLATES
# =====================================================

TEMPLATES = [

    {

        "BACKEND":
        "django.template.backends.django.DjangoTemplates",


        "DIRS":
        [
            BASE_DIR / "templates"
        ],


        "APP_DIRS":
        True,


        "OPTIONS":
        {

            "context_processors":
            [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
                "apps.usuarios.context_processors.usuario_contexto",
                "apps.configuracion.context_processors.emergencia_contexto",
                "apps.configuracion.context_processors.contacto_contexto",

            ],

        },

    },

]


# =====================================================
# WSGI / ASGI
# =====================================================

WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"



# =====================================================
# BASE DE DATOS POSTGRESQL
# =====================================================

DATABASES = {

    "default":

    {

        "ENGINE":
        "django.db.backends.sqlite3",


        "NAME":
        BASE_DIR / "db.sqlite3",

    }

}
# =====================================================
# VALIDACIONES DE PASSWORD
# =====================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },


    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
    },


    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },


    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },

]



# =====================================================
# IDIOMA
# =====================================================

LANGUAGE_CODE = "es"

TIME_ZONE = "America/Guayaquil"

USE_I18N = True

USE_TZ = True



# =====================================================
# ARCHIVOS ESTATICOS
# =====================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [

    BASE_DIR / "static"

]


STATIC_ROOT = BASE_DIR / "staticfiles"



# =====================================================
# MEDIA
# =====================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"



# =====================================================
# MODELOS
# =====================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)



# =====================================================
# CRISPY FORMS
# =====================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = [

    "bootstrap5"

]


CRISPY_TEMPLATE_PACK = "bootstrap5"



# =====================================================
# AUTENTICACION
# =====================================================

AUTHENTICATION_BACKENDS = [

    "django.contrib.auth.backends.ModelBackend",

    "allauth.account.auth_backends.AuthenticationBackend",

]


SITE_ID = 1



LOGIN_URL = "usuarios:login"

LOGIN_REDIRECT_URL = "usuarios:panel"

LOGOUT_REDIRECT_URL = "pagina:inicio"


# =====================================================
# DJANGO ALLAUTH
# =====================================================

ACCOUNT_LOGIN_METHODS = {

    "email",

    "username",

}


ACCOUNT_SIGNUP_FIELDS = [

    "email*",

    "password1*",

    "password2*",

]

ACCOUNT_EMAIL_VERIFICATION = "optional"
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://127.0.0.1:6379/1")
CELERY_TIMEZONE = TIME_ZONE
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
CONTACT_RECIPIENT_EMAIL = env("CONTACT_RECIPIENT_EMAIL", default="alexismacas2020@gmail.com")
CLINICA_NOMBRE = env("CLINICA_NOMBRE", default="Clínica Reina del Cisne")
CLINICA_DIRECCION = env("CLINICA_DIRECCION", default="Centro Médico Reina")





# =====================================================
# GOOGLE LOGIN
# =====================================================

SOCIALACCOUNT_PROVIDERS = {


    "google":

    {


        "SCOPE":

        [

            "profile",

            "email",

        ],



        "AUTH_PARAMS":

        {

            "access_type":
            "online",

            "prompt":
            "select_account",

        },

    }

}

GOOGLE_OAUTH_CLIENT_ID = env("GOOGLE_OAUTH_CLIENT_ID", default=env("GOOGLE_CLIENT_ID", default=""))
GOOGLE_OAUTH_CLIENT_SECRET = env("GOOGLE_OAUTH_CLIENT_SECRET", default=env("GOOGLE_CLIENT_SECRET", default=""))
if GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET:
    SOCIALACCOUNT_PROVIDERS["google"]["APP"] = {
        "client_id": GOOGLE_OAUTH_CLIENT_ID,
        "secret": GOOGLE_OAUTH_CLIENT_SECRET,
        "key": "",
    }
SOCIALACCOUNT_PROVIDERS["google"]["OAUTH_PKCE_ENABLED"] = True
