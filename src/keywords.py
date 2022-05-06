from concurrent.futures import ThreadPoolExecutor
import logging
import os
from selenium import webdriver
from typing import Dict, List

import config
from src import driver_module
from src.links import getLinks

logger = logging.getLogger(__name__)


def getKeywordsStats():
    """ Gets all keywords statistics by threads and write it to file """
    logger.info("Getting keywords statistics.")
    __createOutputDirIfNotExists()
    
    splitted_keywords = getSplittedKeywords()
    with ThreadPoolExecutor(config.NUMBER_OF_THREADS) as executor:
        executor.map(keywordsThreadFunc, splitted_keywords, range(
            config.NUMBER_OF_THREADS))

    concatResultsIntoOneFile()


def keywordsThreadFunc(keywords: List[str], thread_num: int = 0):
    """ Func to get all stata for keywords list and write it to file """
    logger.info(f"Started thread {thread_num}")

    driver = driver_module.getWebDriver()
    with open(f"output/{config.CURRENT_DATE_STR}/results_{config.CURRENT_DATETIME_STR}_{thread_num}.csv", 'w') as wr:
        wr.write("Keyword," +
                 ",".join(config.APP_LINKS) + "\n")
        for i, keyword in enumerate(keywords):
            if i % 10 == 0:
                logger.info(f"Thread {thread_num} - {i}")
                wr.flush()
                os.fsync(wr.fileno())

            keyword_stats = getKeywordStatistics(
                keyword=keyword, driver=driver, thread_num=thread_num)
            s = keyword + "," + \
                ",".join(
                    list(
                        map(lambda x: str(keyword_stats[x]), config.APP_LINKS))
                ) + "\n"
            wr.write(s)
            # break

    logger.info(f"Finished thread {thread_num}")
    driver.close()


def getKeywords() -> List[str]:
    """ Returns list of keywords. """
    with open(config.KEYWORD_FILE_PATH, 'r') as r:
        lines = r.readlines()
        return [line.strip() for line in lines]


def getSplittedKeywords() -> List[List[str]]:
    """ Returns lists of keywords splitted approximately equal by the number of threads """
    keywords = getKeywords()
    k, m = divmod(len(keywords), config.NUMBER_OF_THREADS)
    return [keywords[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(config.NUMBER_OF_THREADS)]


def getKeywordStatistics(keyword: str, driver: webdriver.Chrome, thread_num: int) -> Dict[str, int]:
    """ Returns statistic for `keyword`. It is dict. 
    The key is app link, value is position in google play store (0 if not exists). """
    links = getLinks(keyword=keyword, driver=driver, thread_num=thread_num)
    app_links = config.APP_LINKS
    app_links: List[str]

    output = {}

    for app_link in app_links:
        try:
            output[app_link] = links.index(app_link) + 1
        except ValueError:
            output[app_link] = 0

    return output


def concatResultsIntoOneFile():
    """ Merges results from all thread results files to one. """
    logger.info("Merging data into one file.")
    __createOutputDirIfNotExists()

    with open(f"output/{config.CURRENT_DATE_STR}/results_{config.CURRENT_DATETIME_STR}.csv", 'w') as wr:
        wr.write("Keyword," +
                 ",".join(config.APP_LINKS) + "\n")
        for i in range(config.NUMBER_OF_THREADS):
            with open(f"output/{config.CURRENT_DATE_STR}/results_{config.CURRENT_DATETIME_STR}_{i}.csv", 'r') as r:
                # Skip header line
                r.readline()

                wr.write(r.read())


def __createOutputDirIfNotExists():
    """ Creates output directory if it is not exists """
    if not os.path.isdir(f"output/{config.CURRENT_DATE_STR}"):
        os.mkdir(f"output/{config.CURRENT_DATE_STR}")