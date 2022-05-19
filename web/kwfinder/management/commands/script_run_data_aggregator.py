from django.core.management.base import BaseCommand, CommandParser

from src.keywords import mergeKeywordStatsForDays
from web.kwfinder import models


class Command(BaseCommand):
    help = 'Aggregates stats for a given day for uploaded apps for keywords'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("day", type=str)

    def handle(self, *args, **options):
        app_types = models.AppType.objects.all()
        for app_type in app_types:
            mergeKeywordStatsForDays(day=options['day'], app_type_id=app_type.id)
