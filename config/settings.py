from .base import *


# =====================================================
# CONFIGURACIÓN DE PRODUCCIÓN
# =====================================================

DEBUG = False


# =====================================================
# HOSTS PERMITIDOS
# =====================================================

ALLOWED_HOSTS = [
    "clinica-hhvc.onrender.com",
    "localhost",
    "127.0.0.1",
]


# =====================================================
# CSRF - DOMINIOS CONFIABLES
# =====================================================

CSRF_TRUSTED_ORIGINS = [
    "https://clinica-hhvc.onrender.com",
]


# =====================================================
# CONFIGURACIÓN HTTPS PARA RENDER
# =====================================================

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

USE_X_FORWARDED_HOST = True


# =====================================================
# COOKIES SEGURAS
# =====================================================

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# =====================================================
# TEMPLATES
# =====================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.usuarios.context_processors.usuario_contexto",
            ],
        },
    },
]