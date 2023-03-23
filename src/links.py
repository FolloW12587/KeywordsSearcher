import logging

from typing import List

from exceptions import LinksNotFound
from web.kwfinder.services.googlePlayServicePlain import GooglePlayService
from web.kwfinder import models

logger = logging.getLogger(__name__)


def getGoogleLinks(keyword: str, strore_attributes: str,
                   thread_num: int = 0) -> List[str]:
    """ Uploads and returns links by the given `keyword`. """
    gPS = GooglePlayService(
        base_url=__getGoogleBaseUrl(), thread_num=thread_num)

    links = gPS.getAllAppLinks(keyword=keyword, attributes=strore_attributes)
    logger.info(f"{len(links)} links loaded in thread {thread_num}")
    if len(links) == 0:
        raise LinksNotFound("Didn't find any links. Try angain")

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
