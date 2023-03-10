import logging
from django.core.management.base import BaseCommand

from src.asoworld import update_orders


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updates ASO World orders data'

    def handle(self, *args, **options):
        logger.info("Starting update ASO World orders data")
        update_orders()
