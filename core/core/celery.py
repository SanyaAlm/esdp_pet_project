import os
from datetime import timedelta

from celery import Celery
from core import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "check_discounts_expiry": {
        "task": "api.tasks.check_expiration",
        "schedule": timedelta(seconds=10),
    },
    "cleanup_old_task_metadata": {
        "task": "api.tasks.cleanup_old_task_metadata",
        "schedule": timedelta(minutes=1),
    },
}

app.conf.result_expires = 60
