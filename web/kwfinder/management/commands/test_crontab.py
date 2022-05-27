import logging
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'This command exists just for testing crontab'

    def handle(self, *args, **options):
        logger.info("Hello world!")
