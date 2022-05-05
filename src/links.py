from selenium import webdriver
from typing import List

from services.googlePlayService import GooglePlayService


def getLinks(keyword: str, driver: webdriver.Chrome, thread_num: int) -> List[str]:
    """ Uploads and returns links by the `keyword`, set in `settings.json`. """
    gPS = GooglePlayService(driver=driver, thread_num=thread_num)
    gPS.openStoreSearchPage(keyword=keyword)
    gPS.scrollPageToEnd()
    links = gPS.getAllAppLinks()
    return links


def saveLinks(links: List[str]):
    """ Saves all links in `links.csv` file """
    with open("output/links.csv", 'w') as wr:
        wr.write('position,url\n')
        for i, url in enumerate(links):
            wr.write(f'{i+1},{url}\n')
