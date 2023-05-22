import logging
from time import sleep

from django.core.management.base import BaseCommand

from src.apps_state import check_app
from web.kwfinder import models
from web.kwfinder.services.proxy.mobile_proxy import MobileProxy

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Checks apps state (banned / not banned) and get its icon'

    def handle(self, *args, **options):
        logger.info("Checking apps state!")

        apps = models.App.objects.filter(is_active=True)
        proxy = MobileProxy()
        for app in apps:
            check_app(app, proxy=proxy)
            sleep(2)
