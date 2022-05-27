import logging
from django.core.management.base import BaseCommand, CommandParser

from src.keywords import getKeywordsStatsSelenium
from web.kwfinder import models


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Uploads and saves stats for apps for keywords \
        for app type with given app_type_id'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("app_type_id", type=int)

    def handle(self, *args, **options):
        try:
            models.AppType.objects.get(id=options['app_type_id'])
        except models.AppType.DoesNotExist:
            logger.error(
                f"App type with id {options['app_type_id']} doesn't exists!")
            return
        except Exception as e:
            logger.exception(e)
            return

        getKeywordsStatsSelenium(app_type_id=options['app_type_id'])
