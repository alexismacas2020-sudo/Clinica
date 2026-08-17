from .base import *


DEBUG = False


ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "[::1]",
    "clinica-hhvc.onrender.com",
    ".onrender.com",
    ".ngrok-free.app",
    ".ngrok-free.dev",
    ".ngrok.app",
    ".ngrok.io",
]


CSRF_TRUSTED_ORIGINS = [
    "https://clinica-hhvc.onrender.com",
    "https://*.onrender.com",
    "https://*.ngrok-free.app",
    "https://*.ngrok-free.dev",
    "https://*.ngrok.app",
    "https://*.ngrok.io",
]


SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

USE_X_FORWARDED_HOST = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


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
