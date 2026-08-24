# Envío de correos con Gmail

Activa la verificación en dos pasos y crea una contraseña de aplicación en:
https://myaccount.google.com/apppasswords

Configura `.env` sin compartir la contraseña:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=clinicareina@gmail.com
EMAIL_HOST_PASSWORD=contraseña_de_aplicacion
DEFAULT_FROM_EMAIL=Clínica Reina <clinicareina@gmail.com>
```

Usa la contraseña de aplicación de 16 caracteres, no la contraseña normal de Gmail.

El acceso con el botón "Continuar con Google" usa credenciales OAuth distintas. Consulta `GOOGLE_LOGIN_SETUP.md`.
