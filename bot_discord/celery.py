from datetime import timedelta
from os import environ as env

from celery import Celery

env.setdefault("DJANGO_SETTINGS_MODULE", "bot_discord.settings")


celery_bot_app = Celery("bot_discord")
celery_bot_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_bot_app.autodiscover_tasks()


BEAT_SCHEDULE = celery_bot_app.conf.beat_schedule = {
    "backend_cleanup": {
        "task": "celery.backend_cleanup",
        "schedule": timedelta(days=100),
        "relative": True,
    },
}
