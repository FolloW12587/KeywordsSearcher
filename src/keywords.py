from concurrent.futures import ThreadPoolExecutor
import logging
import os
import re
from selenium import webdriver
from typing import Dict, List

import config
from exceptions import BadDriverException
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
        wr.write(__createFileHeader())
        for i, keyword in enumerate(keywords):
            if i % 10 == 0:
                logger.info(f"Thread {thread_num} - completed {i} out of {len(keywords)}")
                wr.flush()
                os.fsync(wr.fileno())

            try:
                keyword_stats = getKeywordStatistics(
                    keyword=keyword, driver=driver, thread_num=thread_num)
            except BadDriverException as e:
                logger.warning(e)
                logger.info("Reloading driver")
                driver = driver_module.getWebDriver()
                try:
                    keyword_stats = getKeywordStatistics(
                        keyword=keyword, driver=driver, thread_num=thread_num)
                except BadDriverException as e:
                    logger.exception(e)
                    break

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
        wr.write(__createFileHeader())
        for i in range(config.NUMBER_OF_THREADS):
            with open(f"output/{config.CURRENT_DATE_STR}/results_{config.CURRENT_DATETIME_STR}_{i}.csv", 'r') as r:
                # Skip header line
                r.readline()

                wr.write(r.read())


def mergeKeywordStatsForDays(days: List[str]):
    """ Merges all stats for list of `days` into one file """
    if len(days) == 0:
        logger.error("Day is not provided")
        return

    logger.info(f"Starting merging stats for days: {', '.join(days)}")
    path = "output"
    
    if len(days) == 1:
        __createOutputDirIfNotExists(dir_name=days)
        path += f"/{days[0]}"

    stats = getLoadedKeywordsStatsForDays(days=days)
    stats = mergeStats(stats=stats)
    with open(f"{path}/merged_results_{'__'.join(days)}.csv", 'w') as wr:
        wr.write(__createFileHeader())
        for keyword in stats:
            l = [keyword,]
            for app_link in config.APP_LINKS:
                l.append(stats[keyword][app_link] if app_link in stats[keyword] else "0")

            wr.write(",".join(l))


def mergeStats(stats: Dict[str, Dict[str, List[str]]]) -> Dict[str, Dict[str, str]]:
    """ Returns stats merged stats. Every paired keyword-app_link: list is reduced to a str """
    output = {}

    for keyword in stats:
        output[keyword] = {}

        for app_link in stats[keyword]:
            positions = stats[keyword][app_link]

            output[keyword][app_link] = __getMaxRepeatedElementOrConcat(positions)

    return output


def getLoadedKeywordsStatsForDays(days: List[str]) -> Dict[str, Dict[str, List[str]]]:
    """ Returns loaded keywords stats for given `days`. Returned value is a Dict 
    where key is keywords and value is another Dict where key is an app_link 
    and value is a List of its positions during the day.\n
    {
        "<keyword1>": {
            "<app_link1>": [
                "<position1>", ...
            ], ...
        }, ...
    } """
    stats = {}

    for day in days:
        daily_stats = getLoadedKeywordsStatsForDay(day=day)

        for keyword in daily_stats:
            if keyword not in stats:
                stats[keyword] = daily_stats[keyword]
                continue

            for app_link in daily_stats[keyword]:
                if app_link not in stats[keyword]:
                    stats[keyword][app_link] = daily_stats[keyword][app_link]
                    continue

                stats[keyword][app_link] += daily_stats[keyword][app_link]

    return stats


def getLoadedKeywordsStatsForDay(day: str) -> Dict[str, Dict[str, List[str]]]:
    """ Returns loaded keywords stats for a given day. Returned value is a Dict 
    where key is keywords and value is another Dict where key is an app_link 
    and value is a List of its positions during the day.\n
    {
        "<keyword1>": {
            "<app_link1>": [
                "<position1>", ...
            ], ...
        }, ...
    } """
    stats = {}
    stats: Dict[str, Dict[str, List[str]]]

    files = __findStataFiles(day=day)
    logger.info(f"For a day {day} found files {', '.join(files)}")

    for file in files:
        with open(f"output/{day}/{file}", 'r') as r:
            header = r.readline().strip().split(",")

            for line in r:
                l = line.split(",")
                keyword = l[0]
                if keyword not in stats:
                    stats[keyword] = {}

                for i, app_link in enumerate(header):
                    if i == 0:
                        continue

                    if app_link not in stats[keyword]:
                        stats[keyword][app_link] = []

                    stats[keyword][app_link].append(l[i])
        
    return stats


def __findStataFiles(day: str) -> List[str]:
    """ Returns list of filenames that contains full keywords stats for the given `day` """
    # regex for merged files
    files_to_find = f"results_{day}" + r"_\d{2}:\d{2}:\d{2}\.csv"
    files = os.listdir(f"output/{day}")
    return [f for f in files if re.match(files_to_find, f)]


def __createFileHeader() -> str:
    """ Returns heading line for csv file """
    return "Keyword," + ",".join(config.APP_LINKS) + "\n"


def __createOutputDirIfNotExists(dir_name: str = config.CURRENT_DATE_STR):
    """ Creates output directory if it is not exists """
    if not os.path.isdir(f"output/{dir_name}"):
        os.mkdir(f"output/{dir_name}")


def __getMaxRepeatedElementOrConcat(l: List[str]) -> str:
    if len(l) == 0:
        return "0"

    s = set(l)
    if len(l) == len(s):
        return ";".join(l)

    return max(s, key=l.count)
