import logging
from time import sleep
from typing import List
from selenium import webdriver
import selenium

from django.conf import settings

logger = logging.getLogger(__name__)


class GooglePlayService:
    """ Class to manage google store service """

    def __init__(self, driver: webdriver.Chrome,
                 base_url: str, thread_num: int = 0) -> None:
        self.base_url = base_url
        self.driver = driver
        self.thread_num = thread_num

    def openStoreSearchPage(self, keyword: str, attributes: str) -> bool:
        """ Opens google store search page with given keyword. 
        \nReturns `False` if Timeout exception was raised. """
        url = f"{self.base_url}&q={keyword}&{attributes}"
        try:
            self.driver.get(url)
        except selenium.common.exceptions.TimeoutException:
            logger.warning(
                f"Page not loaded properly in thread {self.thread_num}!")
            try:
                sleep(settings.TIME_TO_SLEEP)
                self.driver.get(url)
            except selenium.common.exceptions.TimeoutException:
                logger.error(
                    f"Can't load page {url} in thread {self.thread_num}")
                return False
            except Exception as e:
                logger.exception(e)
                return False

        except Exception as e:
            logger.exception(e)
            return False

        return True

    def scrollPageToEnd(self) -> bool:
        """ Scrolles page till the end and waiting for the uploads. 
        Returns `False` if Timeout exception was raised. """
        try:
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight")
        except selenium.common.exceptions.JavascriptException:
            # If first time not loaded - try to reload and warn
            logger.warning(
                f"Page not loaded properly in thread {self.thread_num} scrolling attempt!")
            try:
                self.driver.refresh()
                last_height = self.driver.execute_script(
                    "return document.body.scrollHeight")
            except (selenium.common.exceptions.JavascriptException,\
                    selenium.common.exceptions.TimeoutException) as e:
                # if second time not loaded - log error and return
                logger.error(
                    f"Can't load page {self.driver.current_url} in thread {self.thread_num} scrolling attempt. Exception {e}")
                return False
            except Exception as e:
                logger.exception(e)
                return False
        except Exception as e:
            logger.exception(e)
            return False

        while True:
            # Scroll down to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            # Hxlbvc
            sleep(settings.TIME_TO_SLEEP)
            while len(self.driver.find_elements_by_class_name("Hxlbvc")):
                sleep(settings.TIME_TO_SLEEP/2)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return True

    def getAllAppLinks(self) -> List[str]:
        """ Retruns list of all apps' links from the opened store page. """
        links = self.driver.find_elements_by_class_name("Gy4nib")
        return [x.get_attribute('href') for x in links]
