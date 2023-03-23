import logging
from django.core.management.base import BaseCommand

from src.keywords import getKeywordsStats


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Uploads and saves stats for apps by keywords'

    def handle(self, *args, **options):
        getKeywordsStats()
