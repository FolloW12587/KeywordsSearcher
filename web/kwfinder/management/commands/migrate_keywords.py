import argparse
from io import TextIOWrapper
import logging
from django.core.management.base import BaseCommand, CommandParser

from web.kwfinder import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrates keywords from given path to given app type'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("csvfile", type=argparse.FileType('r'))
        parser.add_argument("app_type_id", type=int)

    def handle(self, *args, **options):
        try:
            app_type = models.AppType.objects.get(id=options['app_type_id'])
        except models.AppType.DoesNotExist as e:
            logger.error(
                f"App type with id {options['app_type_id']} doesn't exists!")
            return
        except Exception as e:
            logger.exception(e)
            return

        csvfile = options['csvfile']
        csvfile: TextIOWrapper

        keywords = []
        for line in csvfile:
            keywords.append(models.Keyword(
                name=line.strip(),
                app_type=app_type
            ))

        models.Keyword.objects.bulk_create(keywords)
