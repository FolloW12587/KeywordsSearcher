import logging
from django.core.management.base import BaseCommand

from web.kwfinder import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fixes daily aggregated data: deletes instances where \
        app and keyword are not paired and position is 0'

    def handle(self, *args, **options):
        logger.info("Starting fixing daily aggregated stata!")
        data = models.DailyAggregatedPositionData.objects.select_related(
            'app', 'keyword').all()

        count = 0

        for d in data:
            if d.position != 0:
                continue

            app = d.app
            keyword = d.keyword

            if not app.keywords.contains(keyword):
                count += 1
                d.delete()

        logger.info(f"Ended fixing stata. Deleted {count}")
