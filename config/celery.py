import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("clinica")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "recordatorios-email-cada-hora": {
        "task": "apps.citas.tasks.enviar_recordatorios_email",
        "schedule": crontab(minute=0),
    }
}
