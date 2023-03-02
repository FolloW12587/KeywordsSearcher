from django.core.management.base import BaseCommand, CommandParser
import logging

from src.keywords import mergeKeywordStatsForDays
from web.kwfinder import models


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Aggregates stats for a given day for uploaded apps for keywords'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("day", type=str)

    def handle(self, *args, **options):
        logger.info(
            f"Starting aggregate stats for {options['day']} for uploaded stats for keywords.")
        app_types = models.AppType.objects.all()
        for app_type in app_types:
            mergeKeywordStatsForDays(
                day=options['day'], app_type_id=app_type.id)
