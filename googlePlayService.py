from time import sleep
from typing import List
# import requests
from selenium import webdriver

import config


class GooglePlayService:
    """ Class to manage google store service """
    def __init__(self, driver: webdriver.Chrome) -> None:
        self.base_url = config.URL
        self.driver = driver
        # self.url = "https://api.ipify.org?format=json"

    def openStoreSearchPage(self, keyword: str=config.SETTINGS['keyword']):
        """ Opens google store search page with given keyword.
        By `default` it is set in `settings.json`. """
        url = self.base_url.format(keyword=keyword)
        self.driver.get(url)
        # sleep(config.SETTINGS['time_to_sleep'])

    def scrollPageToEnd(self):
        """ Scrolles page till the end and waiting for the uploads. """
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            # Hxlbvc
            sleep(config.SETTINGS['time_to_sleep']/2)
            while len(self.driver.find_elements_by_class_name("Hxlbvc")):
                sleep(config.SETTINGS['time_to_sleep']/4)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def getAllAppLinks(self) -> List[str]:
        """ Retruns list of all apps' links from the opened store page. """
        links = self.driver.find_elements_by_class_name("poRVub")
        return [x.get_attribute('href') for x in links]
