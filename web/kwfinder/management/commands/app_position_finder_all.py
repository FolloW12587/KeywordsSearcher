import logging
from django.core.management.base import BaseCommand

from src.keywords import getKeywordsStats
from web.kwfinder import models


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Gets all app types that has any active app.\
        Uploads and saves stats for every type.'

    def handle(self, *args, **options):
        app_type_ids = models.App.objects.filter(is_active=True).\
            values_list('app_type', flat=True).distinct()

        for app_type_id in app_type_ids:
            getKeywordsStats(app_type_id=app_type_id)
