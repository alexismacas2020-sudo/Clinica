from .base import *


# Nunca se debe mostrar la pagina de depuracion en produccion.
DEBUG = False

# Render recibe la cadena de conexion de Supabase mediante DATABASE_URL.
# No se usa SQLite en produccion porque el sistema de archivos de Render
# es efimero y la base se perderia al reiniciar o volver a desplegar.
DATABASES = {
    "default": env.db("DATABASE_URL"),
}
DATABASES["default"].setdefault("OPTIONS", {})["sslmode"] = env(
    "DATABASE_SSLMODE",
    default="require",
)

ALLOWED_HOSTS = list(dict.fromkeys([
    "clinica-hhvc.onrender.com",
    "localhost",
    "127.0.0.1",
    *env.list("ALLOWED_HOSTS", default=[]),
]))

CSRF_TRUSTED_ORIGINS = list(dict.fromkeys([
    "https://clinica-hhvc.onrender.com",
    *env.list("CSRF_TRUSTED_ORIGINS", default=[]),
]))

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
