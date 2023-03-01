import logging
from django.core.management.base import BaseCommand

from src.apps_state import check_app
from web.kwfinder import models


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Checks apps state (banned / not banned) and get its icon'

    def handle(self, *args, **options):
        logger.info("Checking apps state!")

        apps = models.App.objects.filter(is_active=True)
        for app in apps:
            check_app(app)
