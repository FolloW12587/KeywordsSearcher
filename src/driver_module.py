from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import config


def testDriver():
    driver = getWebDriver()

    driver.get("https://google.com")
    sleep(5)
    driver.close()


def getWebDriver() -> webdriver.Chrome:
    """ Returns Chrome webdriver """
    service = Service(config.DRIVER_PATH)
    options = Options()
    options.headless = config.IS_HEADLESS_MODE
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    return driver