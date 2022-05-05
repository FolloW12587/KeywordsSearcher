import logging
from time import sleep
from typing import List
from selenium import webdriver
import selenium

import config

logger = logging.getLogger(__name__)


class GooglePlayService:
    """ Class to manage google store service """

    def __init__(self, driver: webdriver.Chrome, thread_num: int = 0) -> None:
        self.base_url = config.URL
        self.driver = driver
        self.thread_num = thread_num
        # self.url = "https://api.ipify.org?format=json"

    def openStoreSearchPage(self, keyword: str = config.KEYWORD):
        """ Opens google store search page with given keyword.
        By `default` it is set in `settings.json`. """
        url = self.base_url.format(keyword=keyword)
        try:
            self.driver.get(url)
        except selenium.common.exceptions.TimeoutException:
            logger.warning(
                f"Page not loaded properly in thread {self.thread_num}!")
            try:
                self.driver.refresh()
            except selenium.common.exceptions.TimeoutException:
                logger.error(
                    f"Can't load page {url} in thread {self.thread_num}")
                return

    def scrollPageToEnd(self):
        """ Scrolles page till the end and waiting for the uploads. """
        try:
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight")
        except selenium.common.exceptions.JavascriptException:
            # If first time not loaded - try to reload and warn
            logger.warning(
                f"Page not loaded properly in thread {self.thread_num}!")
            self.driver.refresh()
            try:
                last_height = self.driver.execute_script(
                    "return document.body.scrollHeight")
            except selenium.common.exceptions.JavascriptException:
                # if second time not loaded - log error and return
                logger.error(
                    f"Can't load page {self.driver.current_url} in thread {self.thread_num}")
                return

        while True:
            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            # Hxlbvc
            sleep(config.TIME_TO_SLEEP)
            while len(self.driver.find_elements_by_class_name("Hxlbvc")):
                sleep(config.TIME_TO_SLEEP/2)

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
