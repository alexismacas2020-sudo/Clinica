from .base import *


# Configuracion segura para Render. Estos valores se pueden reemplazar desde
# las variables de entorno sin tener que modificar el codigo.
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["clinica-hhvc.onrender.com"],
)

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["https://clinica-hhvc.onrender.com"],
)

# Render termina HTTPS en su proxy y envia este encabezado a Django.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# WhiteNoise sirve los archivos generados por collectstatic.
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
