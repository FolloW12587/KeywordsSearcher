import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

from web.kwfinder import models


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Deletes non aggregated data that is older then 7 days'

    def handle(self, *args, **options):
        logger.info("Start deleting old data!")
        date = datetime.now() - timedelta(days=7)
        old_runs = models.AppPositionScriptRun.objects.filter(
            started_at__lt=date)

        old_data = models.AppPositionScriptRunData.objects.filter(
            run__id__in=list(old_runs.values_list('id', flat=True)))

        deleted = old_data.delete()
        logger.info(f"End of deleting data! Deleted {deleted}.")
