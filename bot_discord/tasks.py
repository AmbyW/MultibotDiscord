from datetime import date, timedelta
from celery import shared_task
from celery.utils.log import get_task_logger
from celery.schedules import crontab

from .models import DailyContribution, Kingdom
from .utils.land import get_lands_data, make_urls, LAND_ID
from .celery import celery_bot_app

logger = get_task_logger(__name__)


@shared_task()
def update_contributions():
    yesterday = date.today() - timedelta(days=1)
    contributions = get_lands_data(make_urls(yesterday, yesterday))
    dailys = []
    for contribution in contributions:
        dailys.append(DailyContribution(
            date=yesterday,
            contribution=contribution["total"],
            kingdom=Kingdom.objects.get(lok_id=contribution["kingdomId"]),
            land_id=LAND_ID
        ))
    DailyContribution.objects.bulk_create(dailys)

    return True


celery_bot_app.conf.beat_schedule = {
    "add-every-day": {
        "task": "bot_discord.tasks.update_contributionsv",
        "schedule": crontab(minute="0", hour="0"),
    }
}
