# Recordatorios de WhatsApp

## Configuración

Completa en `.env`:

```env
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
WHATSAPP_ACCESS_TOKEN=token_de_meta
WHATSAPP_PHONE_NUMBER_ID=id_del_numero
WHATSAPP_API_VERSION=v23.0
WHATSAPP_TEMPLATE_NAME=recordatorio_cita
WHATSAPP_LANGUAGE_CODE=es
CLINICA_NOMBRE=Clínica Reina del Cisne
CLINICA_DIRECCION=Centro Médico Reina
```

La plantilla aprobada en Meta debe recibir siete variables, en este orden: paciente, clínica, fecha, hora, médico, especialidad y dirección. El texto aprobado debe incluir la recomendación de llegar 15 minutos antes y las instrucciones para cancelar o reagendar.

## Procesos necesarios

En terminales separadas:

```powershell
.\venv\Scripts\python.exe manage.py runserver
redis-server
.\venv\Scripts\celery.exe -A config worker -l info --pool=solo
.\venv\Scripts\celery.exe -A config beat -l info
```

En Windows se utiliza `--pool=solo`. En Linux puede omitirse.

## Prueba manual sin esperar un día

Configura una cita pendiente o confirmada para mañana, con un teléfono válido en el perfil del paciente. Después ejecuta:

```powershell
.\venv\Scripts\python.exe manage.py shell -c "from apps.citas.tasks import enviar_recordatorios_whatsapp; print(enviar_recordatorios_whatsapp())"
```

Sin credenciales de Meta, la cita conservará `recordatorio_whatsapp_enviado=False` y registrará un error seguro para permitir otro intento.

## Comprobaciones

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py test
```
