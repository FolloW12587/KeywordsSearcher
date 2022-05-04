from time import sleep
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import config
from googlePlayService import GooglePlayService


def main():
    """ Main function """
    driver = getWebDriver()

    gPS = GooglePlayService(driver=driver)
    gPS.openStoreSearchPage()
    gPS.scrollPageToEnd()
    links = gPS.getAllAppLinks()
    saveLinks(links)

    driver.close()


def testDriver():
    driver = getWebDriver()

    driver.get("https://google.com")
    sleep(5)
    driver.close()


def getWebDriver() -> webdriver.Chrome:
    service = Service(config.SETTINGS['driver_path'])
    return webdriver.Chrome(service=service)


def saveLinks(links: List[str]):
    """ Saves all links in `links.csv` file """
    with open("links.csv", 'w') as wr:
        wr.write('position,url\n')
        for i, url in enumerate(links):
            wr.write(f'{i+1},{url}\n')

if __name__ == "__main__":
    main()
