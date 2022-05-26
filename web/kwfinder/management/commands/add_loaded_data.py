import argparse
from io import TextIOWrapper
import logging
from typing import Dict
from django.core.management.base import BaseCommand, CommandParser

from web.kwfinder import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Adds data from given csvfile to script run with given id'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("csvfile", type=argparse.FileType('r'))
        parser.add_argument("script_run_id", type=int)

    def handle(self, *args, **options):
        try:
            script_run = models.AppPositionScriptRun.objects.get(
                id=options['script_run_id'])
        except models.AppPositionScriptRun.DoesNotExist as e:
            logger.error(
                f"Script run with id {options['script_run_id']} doesn't exists!")
            return
        except Exception as e:
            logger.exception(e)
            return

        csvfile = options['csvfile']
        csvfile: TextIOWrapper

        link_matching = self.__getLinkMatching(
            app_type_id=script_run.app_type.id)
        links = csvfile.readline().strip().split(',')[1:]

        data = []
        for line in csvfile:
            splitted_line = line.strip().split(",")

            try:
                keyword = models.Keyword.objects.get(name=splitted_line[0])
            except models.Keyword.DoesNotExist as e:
                logger.warning(f"Keyword {splitted_line[0]} doesn't exists!")
                continue

            for i, position in enumerate(splitted_line[1:]):
                data.append(
                    models.AppPositionScriptRunData(
                        run=script_run,
                        keyword=keyword,
                        app=link_matching[links[i]],
                        position=int(position)
                    )
                )

        models.AppPositionScriptRunData.objects.bulk_create(data)

    def __getLinkMatching(self, app_type_id: int) -> Dict[str, models.App]:
        """ Returns dict where key is app link and value is app instance 
        for given app_type id """
        link_matching = {}

        apps = models.App.objects.filter(app_type__id=app_type_id).all()
        for app in apps:
            link_matching[app.link] = app

        return link_matching
