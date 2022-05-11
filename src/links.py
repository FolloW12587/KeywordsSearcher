import logging
from time import sleep
from selenium import webdriver
from typing import List, Optional

import config
from exceptions import BadDriverException
from services.googlePlayService import GooglePlayService
from src.driver_module import getWebDriver

logger = logging.getLogger(__name__)


def getLinks(keyword: str, driver: webdriver.Chrome, thread_num: int=0) -> List[str]:
    """ Uploads and returns links by the given `keyword`. """
    gPS = GooglePlayService(driver=driver, thread_num=thread_num)
    if not gPS.openStoreSearchPage(keyword=keyword):
        # sleep(config.TIME_TO_SLEEP)
        raise BadDriverException("Bad sequence of requests. Driver needs to be reloaded")
    if not gPS.scrollPageToEnd():
        # logger.warning("Bad request scrolling")
        # sleep(config.TIME_TO_SLEEP)
        # return []
        raise BadDriverException("Bad sequence of requests. Driver needs to be reloaded")
    links = gPS.getAllAppLinks()
    return links


def saveLinks(links: List[str]):
    """ Saves all links in `links.csv` file """
    logger.info("Saving links.")

    with open("output/links.csv", 'w') as wr:
        wr.write('position,url\n')
        for i, url in enumerate(links):
            wr.write(f'{i+1},{url}\n')


def uploadLinks():
    """ Uploads links by the `keyword` that is set in `settings.json`.
    Then saves them to `output/links.csv`. """
    logger.info("Uploading links.")

    driver = getWebDriver()
    links = getLinks(keyword=config.KEYWORD, driver=driver)
    saveLinks(links)
