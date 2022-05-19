from django.core.management.base import BaseCommand, CommandParser

from src.keywords import getKeywordsStats


class Command(BaseCommand):
    help = 'Uploads and saves stats for apps for keywords \
        for app type with given app_type_id'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("app_type_id", type=int)

    def handle(self, *args, **options):
        getKeywordsStats(app_type_id=options['app_type_id'])
