import argparse
import logging
from django.core.management.base import BaseCommand, CommandParser


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrates keywords from given path to given app type'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("csvfile", type=argparse.FileType('r'))

    def handle(self, *args, **options):
        logger.error(f"Not implemented!")
