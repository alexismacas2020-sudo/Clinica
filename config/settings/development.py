from .base import *


DEBUG = True


ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1"
]

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

            ],

        },

    },

]
