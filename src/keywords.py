from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from selenium import webdriver
from typing import List

# import settings
from django.conf import settings
from exceptions import BadDriverException
from src import driver_module
from src.links import getGoogleLinks
from web.kwfinder import models

logger = logging.getLogger(__name__)


def getKeywordsStats(app_type_id: int):
    """ Gets all keywords statistics for app_type with given `app_type_id`
    by threads and write it to file """
    logger.info("Getting keywords statistics.")

    app_type = models.AppType.objects.get(id=app_type_id)
    script_run = models.AppPositionScriptRun(app_type=app_type)
    script_run.save()
    splitted_keywords = __getSplittedKeywords(app_type=app_type)
    with ThreadPoolExecutor(settings.NUMBER_OF_THREADS) as executor:
        executor.map(
            __keywordsThreadFunc,
            splitted_keywords,
            [script_run, ] * settings.NUMBER_OF_THREADS,
            range(settings.NUMBER_OF_THREADS)
        )
    script_run.ended_at = datetime.now()
    script_run.save()


def __keywordsThreadFunc(keywords: List[models.Keyword],
                         run: models.AppPositionScriptRun, thread_num: int = 0):
    """ Func to get all stata for given `keywords list` 
    and write it to db for given `run` """
    logger.info(f"Started thread {thread_num} of run with id {run.id}")

    driver = driver_module.getWebDriver()

    for i, keyword in enumerate(keywords):
        if i % 10 == 0:
            logger.info(
                f"Thread {thread_num} - completed {i} out of {len(keywords)}")

        try:
            __getKeywordStatistics(
                keyword=keyword, driver=driver, thread_num=thread_num, run=run)
        except BadDriverException as e:
            logger.warning(e)
            logger.info("Reloading driver")
            driver = driver_module.getWebDriver()
            try:
                __getKeywordStatistics(
                    keyword=keyword, driver=driver, thread_num=thread_num, run=run)
            except BadDriverException as e:
                logger.exception(e)
                break
            
            except Exception as e:
                logger.exception(e)
                break

        except Exception as e:
            logger.exception(e)
            break
        # break

    logger.info(f"Finished thread {thread_num}")
    driver.close()


def __getKeywords(app_type: models.AppType) -> List[models.Keyword]:
    """ Returns list of keywords of given app type. """
    return list(models.Keyword.objects.filter(app_type=app_type).all())


def __getSplittedKeywords(app_type: models.AppType) -> List[List[models.Keyword]]:
    """ Returns lists of keywords splitted approximately 
    equal by the number of threads of given app_type """
    keywords = __getKeywords(app_type=app_type)
    k, m = divmod(len(keywords), settings.NUMBER_OF_THREADS)
    return [keywords[i*k+min(i, m):(i+1)*k+min(i+1, m)]
            for i in range(settings.NUMBER_OF_THREADS)]


def __getKeywordStatistics(keyword: models.Keyword, driver: webdriver.Chrome,
                           thread_num: int, run: models.AppPositionScriptRun):
    """ Returns statistic for `keyword`. It is dict. The key is app link, 
    value is position in google play store (0 if not exists). """
    links = getGoogleLinks(
        keyword=keyword.name, 
        driver=driver,
        thread_num=thread_num, 
        strore_attributes=keyword.app_type.google_store_link_attributes)
    apps = __getApps(app_type=keyword.app_type)

    for app in apps:
        try:
            position = links.index(app.link) + 1
        except ValueError:
            position = 0

        data = models.AppPositionScriptRunData(
            run=run,
            keyword=keyword,
            app=app,
            position=position
        )
        data.save()


def __getApps(app_type: models.AppType) -> List[models.App]:
    """ Returns List of apps that relate to given `app_type` """
    return list(models.App.objects.filter(app_type=app_type).all())


def mergeKeywordStatsForDays(day: str, app_type_id: int):
    """ Merges all stats for a `day` for an app_type
    with given `app_type_id` """

    logger.info(f"Starting merging stats for {day}")
    app_type = models.AppType.objects.get(id=app_type_id)
    runs = models.AppPositionScriptRun.objects.filter(
        app_type=app_type,
        started_at__range=[f"{day} 00:00:00", f"{day} 23:59:59"]).all()
    keywords = models.Keyword.objects.filter(app_type=app_type).all()
    apps = models.App.objects.filter(app_type=app_type).all()

    for keyword in keywords:
        for app in apps:
            __aggregateKeywordStats(
                day=day,
                app=app,
                keyword=keyword,
                runs=runs)


def __aggregateKeywordStats(day: str, app: models.App,
                            keyword: models.Keyword,
                            runs: List[models.AppPositionScriptRun]):
    """ Aggregates stats for given `day` for an `app` and `keyword` 
    in bunch of `runs` """
    data = models.AppPositionScriptRunData.objects.filter(
        keyword=keyword, run__in=runs, app=app).all()
    position = __getMaxRepeatedElementOrAvg([d.position for d in data])

    aggData = models.DailyAggregatedPositionData(
        date=datetime.strptime(day, r'%Y-%m-%d').date(),
        keyword=keyword,
        app=app,
        position=position
    )
    aggData.save()


def __getMaxRepeatedElementOrAvg(l: List[int]) -> int:
    if len(l) == 0:
        return 0

    s = set(l)
    if len(l) == len(s):
        return int(sum(l) / len(l))

    return max(s, key=l.count)
