import logging
from django.core.management.base import BaseCommand

from src.asoworld import update_apps_and_keywords


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updates apps and keywords from ASO World'

    def handle(self, *args, **options):
        logger.info("Starting update apps and keywords!")
        update_apps_and_keywords()
