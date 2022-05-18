from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from django.conf import settings


def testDriver():
    driver = getWebDriver()

    driver.get("https://google.com")
    sleep(5)
    driver.close()


def getWebDriver() -> webdriver.Chrome:
    """ Returns Chrome webdriver """
    service = Service(settings.DRIVER_PATH)
    options = Options()
    options.headless = settings.IS_HEADLESS_MODE
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(settings.TIMEOUT_TIME)
    return driver