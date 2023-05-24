import logging
from time import sleep

from django.core.management.base import BaseCommand

from src.apps_state import check_app
from web.kwfinder import models
from web.kwfinder.services.proxy.simple_proxy import (
    create_proxy_requests_session, get_proxy, safe_proxy_repr)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Checks apps state (banned / not banned) and get its icon'

    def handle(self, *args, **options):
        logger.info("Checking apps state!")

        apps = models.App.objects.filter(is_active=True)
        proxies = get_proxy()
        if not proxies:
            logger.error("Can't find proxy. Aborting!")
            return
        
        session = create_proxy_requests_session(proxy=proxies)
        if not session:
            logger.error(f"Can't create session for proxy {safe_proxy_repr(proxies)}. Aborting!")
            return

        for app in apps:
            check_app(app, session)
            sleep(2)
