from django.core.management.base import BaseCommand
from datetime import date, timedelta
import logging

from src.keitaro import update_keitaro_stats


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updates keitaro statistics for last 5 days'

    def handle(self, *args, **options):
        logger.info("Starting update keitaro stats for last 5 days.")
        date_from = date.today() - timedelta(days=5)
        date_to = date.today()

        update_keitaro_stats(date_from, date_to)
