from concurrent.futures import ThreadPoolExecutor
import logging

import logs
from src.keywords import getKeywordsStats

logger = logging.getLogger(__name__)


def main():
    """ Main function """
    logger.info("Started main function")
    # driver = getWebDriver()
    # # links = getLinks(keyword=config.KEYWORD, driver=driver)
    # # saveLinks(links)

    getKeywordsStats()
    logger.info("Finished")


if __name__ == "__main__":
    main()
