import logging
from django.core.management.base import BaseCommand

from src.asoworld import upload_regions


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Uploads regions for ASO World, saved in `resources/regions.csv`'

    def handle(self, *args, **options):
        logger.info("Starting upload resources from resources/regions.csv")
        upload_regions()
