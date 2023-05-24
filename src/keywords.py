import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from time import sleep
from typing import List

from django.conf import settings
from django.db.models import Count, Q
from django.db.models.query import QuerySet
from requests import Session

from exceptions import LinksNotFound
from src.links import getGoogleLinks
from web.kwfinder import models
from web.kwfinder.services.proxy.simple_proxy import (
    create_proxy_requests_session, get_proxy, safe_proxy_repr)

logger = logging.getLogger(__name__)


def getKeywordsStats():
    """Gets all keywords statistics by threads and writes it to database"""
    logger.info("Getting keywords statistics.")

    script_run = models.AppPositionScriptRun()
    script_run.save()
    splitted_keywords = __getSplittedKeywords()
    with ThreadPoolExecutor(settings.NUMBER_OF_THREADS) as executor:
        executor.map(
            __keywordsThreadFunc,
            splitted_keywords,
            [
                script_run,
            ]
            * settings.NUMBER_OF_THREADS,
            range(settings.NUMBER_OF_THREADS),
        )
    script_run.ended_at = datetime.now()
    script_run.save()


def __keywordsThreadFunc(keywords: List[models.Keyword], 
                         run: models.AppPositionScriptRun, 
                         thread_num: int = 0):
    """Func to get all stata for given `keywords list`
    and write it to db for given `run`"""
    logger.info(f"Started thread {thread_num} of run with id {run.id}")
    proxies = get_proxy()
    if not proxies:
        logger.error("Can't find proxy. Aborting!")
        return
    
    session = create_proxy_requests_session(proxy=proxies)
    if not session:
        logger.error(f"Can't create session for proxy {safe_proxy_repr(proxies)}. Aborting!")
        return

    for i, keyword in enumerate(keywords):
        if i % 10 == 0:
            logger.info(f"Thread {thread_num} - completed {i} out of {len(keywords)}")

        if not __precessKeyword(
            keyword=keyword,
            run=run,
            thread_num=thread_num,
            session=session
        ):
            break

    logger.info(f"Finished thread {thread_num}")


def __precessKeyword(keyword: models.Keyword, 
                     run: models.AppPositionScriptRun,
                     thread_num: int = 0, 
                     session: Session | None = None) -> bool:
    """Processing keyword in thread

    Args:
        keyword (models.Keyword): keyword to process
        run (models.AppPositionScriptRun): run object
        attempt (int, optional): Attempt num. Defaults to 0.
        thread_num (int, optional): Thread num. Defaults to 0.

    Returns:
        Bool: True if processed successfully. Else False.
    """
    sleep(settings.TIME_TO_SLEEP / 2)

    try:
        __getKeywordStatistics(keyword=keyword, thread_num=thread_num, run=run, session=session)

    except LinksNotFound as e:
        logger.warning(e)
        return True

    except Exception as e:
        logger.exception(e)
        return False

    return True

def __getSplittedKeywords() -> List[List[models.Keyword]]:
    """Returns lists of keywords splitted approximately
    equal by the number of threads"""
    keywords_qs = models.Keyword.objects.annotate(app_count=Count("app", filter=Q(app__is_active=True))).exclude(
        app_count=0
    )

    keywords = list(keywords_qs)
    k, m = divmod(len(keywords), settings.NUMBER_OF_THREADS)
    return [keywords[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(settings.NUMBER_OF_THREADS)]


def __getKeywordStatistics(keyword: models.Keyword, 
                           thread_num: int, 
                           run: models.AppPositionScriptRun, 
                           session: Session | None = None):
    """Returns statistic for `keyword`. It is dict. The key is app link,
    value is position in google play store (0 if not exists)."""
    if not keyword.region.google_store_link_attributes:
        logger.warning(f"Keyword {keyword} doesn't contain Google play market attributes!")
        return

    links = getGoogleLinks(
        keyword=keyword.name, 
        thread_num=thread_num, 
        strore_attributes=keyword.region.google_store_link_attributes, 
        session=session
    )
    apps = keyword.app_set.filter(is_active=True)  # type: ignore
    apps: QuerySet[models.App]

    if apps.count() == 0:
        logger.warning(f"No apps found for keyword {keyword}!")
        return

    for app in apps:
        try:
            position = links.index(app.link) + 1
        except ValueError:
            position = 0

        data = models.AppPositionScriptRunData(run=run, keyword=keyword, app=app, position=position)
        data.save()


def mergeKeywordStatsForDays(day: str):
    """Merges all stats for a `day`"""
    logger.info(f"Starting merging stats for {day}.")
    runs = list(
        models.AppPositionScriptRun.objects.filter(started_at__range=[f"{day} 00:00:00", f"{day} 23:59:59"]).all()
    )
    apps = models.App.objects.all()

    data = []
    for app in apps:
        for keyword in app.keywords.all():
            data.append(__aggregateKeywordStats(day=day, app=app, keyword=keyword, runs=runs))

    models.DailyAggregatedPositionData.objects.bulk_create(data)
    logger.info(f"Merging is ended. {len(data)} instances created.")


def __aggregateKeywordStats(
    day: str, app: models.App, keyword: models.Keyword, runs: list[models.AppPositionScriptRun]
) -> models.DailyAggregatedPositionData:
    """Aggregates stats for given `day` for an `app` and `keyword`
    in bunch of `runs` and returns DailyAggregatedPositionData instance"""
    data = models.AppPositionScriptRunData.objects.filter(keyword=keyword, run__in=runs, app=app).all()
    position = __getMaxRepeatedElementOrAvg([d.position for d in data])

    return models.DailyAggregatedPositionData(
        date=datetime.strptime(day, r"%Y-%m-%d").date(), keyword=keyword, app=app, position=position
    )


def __getMaxRepeatedElementOrAvg(l: List[int]) -> int:
    if len(l) == 0:
        return 0

    s = set(l)
    if len(l) == len(s):
        if len(l) == 1:
            return l[0]
        if 0 in l:
            return int(sum(l) / (len(l) - 1))
        return int(sum(l) / len(l))

    return max(s, key=l.count)
