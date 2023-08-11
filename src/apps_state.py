import logging
import random

import requests
from bs4 import BeautifulSoup
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from web.kwfinder import models
from web.kwfinder.services.telegram.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)


def check_app(app: models.App, session: requests.Session):
    """ Checks app state (banned / or not banned) and updates its icon

    Args:
        app (App): app to check
    """
    logger.info(f"Checking app {app.name}_{app.num}.")

    try:
        r = session.get(app.link)
    except Exception as e:
        logger.exception(e)
        logger.warning("Failed to check app's state!")
        return

    if r.status_code == 404:
        logger.info(f"App {app.name}_{app.num} is most likely banned!")
        if app.is_active:
            bot = TelegramBot()
            bot.sendMessage(
                f"Приложение *{TelegramBot.translateMessage(app.name)}* с номером *{TelegramBot.translateMessage(app.num)}* забаненно {random.choice(TelegramBot.SAD_FACES_EMOJIS)}",
                parse_mode='MarkdownV2')
        app.is_active = False
        app.save()
        return

    parsed_html = BeautifulSoup(r.text, features="html.parser")
    img = parsed_html.find('img', class_='T75of nm4vBd arM4bb')

    __update_icon(app=app, img=img, session=session)


def __update_icon(app: models.App, img, session: requests.Session):
    if not img:
        logger.warning("Failed to update icon!")
        return

    img_data = session.get(img['src'])

    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(img_data.content)
    img_temp.flush()

    try:
        app.icon.save(f"{app.name}_icon.png", File(img_temp), save=True)
    except Exception as e:
        logger.exception(e)
        logger.warning("Failed to update icon!")
