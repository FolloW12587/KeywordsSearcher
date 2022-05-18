import logging

from selenium import webdriver
from typing import List

from exceptions import BadDriverException
from web.kwfinder.services.googlePlayService import GooglePlayService
from web.kwfinder import models

logger = logging.getLogger(__name__)


def getGoogleLinks(keyword: str, driver: webdriver.Chrome, 
                   strore_attributes: str, thread_num: int = 0) -> List[str]:
    """ Uploads and returns links by the given `keyword`. """

    gPS = GooglePlayService(
        driver=driver, base_url=__getGoogleBaseUrl(), thread_num=thread_num)
    if not gPS.openStoreSearchPage(keyword=keyword, 
                                   attributes=strore_attributes):
        raise BadDriverException(
            "Bad sequence of requests. Driver needs to be reloaded")
    if not gPS.scrollPageToEnd():
        raise BadDriverException(
            "Bad sequence of requests. Driver needs to be reloaded")
    links = gPS.getAllAppLinks()
    return links


def __getGoogleBaseUrl() -> str:
    """ Returns base search link for platform Google """
    platform = models.AppPlatform.objects.get(name='Google')
    return platform.base_store_link

# def saveLinks(links: List[str]):
#     """ Saves all links in `links.csv` file """
#     logger.info("Saving links.")

#     with open("output/links.csv", 'w') as wr:
#         wr.write('position,url\n')
#         for i, url in enumerate(links):
#             wr.write(f'{i+1},{url}\n')


# def uploadLinks():
#     """ Uploads links by the `keyword` that is set in `settings.json`.
#     Then saves them to `output/links.csv`. """
#     logger.info("Uploading links.")

#     driver = getWebDriver()
#     links = getLinks(keyword=config.KEYWORD, driver=driver)
#     saveLinks(links)
