import logging

import requests
from bs4 import BeautifulSoup
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from web.kwfinder import models
from web.kwfinder.services.proxy.mobile_proxy import MobileProxy

logger = logging.getLogger(__name__)


def check_app(app: models.App, proxy: MobileProxy | None = None):
    """ Checks app state (banned / or not banned) and updates its icon

    Args:
        app (App): app to check
    """
    logger.info(f"Checking app {app.name}_{app.num}.")

    proxies = None if not proxy else proxy.requests_proxies_dict

    try:
        r = requests.get(app.link, proxies=proxies)
    except Exception as e:
        logger.exception(e)
        logger.warning("Failed to check app's state!")
        return

    if r.status_code == 404:
        logger.info(f"App {app.name}_{app.num} is most likely banned!")
        app.is_active = False
        app.save()
        return

    parsed_html = BeautifulSoup(r.text, features="html.parser")
    img = parsed_html.find('img', class_='T75of nm4vBd arM4bb')

    if not img:
        logger.warning("Failed to update icon!")
        return

    img_data = requests.get(img['src'])

    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(img_data.content)
    img_temp.flush()

    try:
        app.icon.save(f"{app.name}_icon.png", File(img_temp), save=True)
    except Exception as e:
        logger.exception(e)
        logger.warning("Failed to update icon!")
