import logging
import os
from time import sleep
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import logs
import config
from googlePlayService import GooglePlayService

logger = logging.getLogger(__name__)


def main():
    """ Main function """
    logger.info("Started main function")
    driver = getWebDriver()
    # links = getLinks(keyword=config.SETTINGS['keyword'], driver=driver)
    # saveLinks(links)

    keywords = getKeywords()[420:]

    with open("results.csv", 'w') as wr:
        wr.write("Keyword," + ",".join(config.SETTINGS['app_links']) + "\n")
        for i, keyword in enumerate(keywords):
            if i % 10 == 0:
                logger.info(f"{i}")
                wr.flush()
                os.fsync(wr.fileno())
                
            keyword_stats = getKeywordStatistics(
                keyword=keyword, driver=driver)
            s = keyword + "," + \
                ",".join(
                    list(
                        map(lambda x: str(keyword_stats[x]), config.SETTINGS['app_links']))
                ) + "\n"
            wr.write(s)
            # break
    
    logger.info("Finished")
    driver.close()


def testDriver():
    driver = getWebDriver()

    driver.get("https://google.com")
    sleep(5)
    driver.close()


def getWebDriver() -> webdriver.Chrome:
    service = Service(config.SETTINGS['driver_path'])
    return webdriver.Chrome(service=service)


def getLinks(keyword: str, driver: webdriver.Chrome) -> List[str]:
    """ Uploads and returns links by the `keyword`, set in `settings.json`. """
    gPS = GooglePlayService(driver=driver)
    gPS.openStoreSearchPage(keyword=keyword)
    gPS.scrollPageToEnd()
    links = gPS.getAllAppLinks()
    return links


def getKeywords() -> List[str]:
    """ Returns list of keywords. """
    with open(config.SETTINGS['keyword_file_path'], 'r') as r:
        lines = r.readlines()
        return [line.strip() for line in lines]


def saveLinks(links: List[str]):
    """ Saves all links in `links.csv` file """
    with open("links.csv", 'w') as wr:
        wr.write('position,url\n')
        for i, url in enumerate(links):
            wr.write(f'{i+1},{url}\n')


def getKeywordStatistics(keyword: str, driver: webdriver.Chrome) -> Dict[str, int]:
    """ Returns statistic for `keyword`. It is dict. The key is app link, value is position in google play store (0 if not exists). """
    links = getLinks(keyword=keyword, driver=driver)
    # saveLinks(links)
    app_links = config.SETTINGS['app_links']
    app_links: List[str]

    output = {}

    for app_link in app_links:
        try:
            output[app_link] = links.index(app_link) + 1
        except ValueError:
            output[app_link] = 0

    return output


if __name__ == "__main__":
    main()
