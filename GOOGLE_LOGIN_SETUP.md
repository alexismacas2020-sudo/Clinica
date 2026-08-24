# Configuración del inicio de sesión con Google

Las credenciales OAuth nunca deben guardarse en Git ni escribirse directamente en este documento.

## Variables de entorno

Configura estos valores únicamente en el archivo local `.env` y en las variables de entorno de Render:

```env
GOOGLE_OAUTH_CLIENT_ID=tu-client-id-de-google
GOOGLE_OAUTH_CLIENT_SECRET=tu-client-secret-de-google
```

El archivo `.env` está excluido del repositorio mediante `.gitignore`.

## Google Cloud Console

1. Crea o selecciona el proyecto de Google Cloud.
2. Configura la pantalla de consentimiento OAuth.
3. Crea credenciales de tipo **ID de cliente OAuth para aplicación web**.
4. Agrega las URL autorizadas de desarrollo y producción.
5. Copia el Client ID y el Client Secret directamente a las variables de entorno.

## Seguridad

Si una credencial aparece en un commit, captura de pantalla o registro compartido, revócala y genera una nueva desde Google Cloud Console.
