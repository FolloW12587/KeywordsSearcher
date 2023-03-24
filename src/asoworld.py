from datetime import datetime, timedelta, timezone
from django.db.models import Sum
import logging
import os
from typing import Any

from web.kwfinder import models
from web.kwfinder.controllers.asoworldAPI import ASOWorldAPIController


logger = logging.getLogger(__name__)


def upload_regions():
    """ Uploads regions from `resources/regions.csv` to ASOWorldRegion table """
    path = "resources/regions.csv"

    if not os.path.isfile(path):
        logger.error(f"File {path} doesn't exist!")
        return

    with open(path, 'r') as regions_file:
        for line in regions_file:
            line_to_split = line[:-1]
            region = models.ASOWorldRegion.objects.filter(
                code=line_to_split.split(";")[0]
            ).first()

            if region:
                continue

            region = models.ASOWorldRegion(*line_to_split.split(";"))
            region.is_app_store_supported = region.is_app_store_supported == 'true'
            region.is_google_play_supported = region.is_google_play_supported == 'true'
            region.save()

    logger.info("Uploaded.")


def update_apps_and_keywords():
    """ Gets all keywords from ASO World. For every keyword, \
        creates app if not exists and adds itself to it. """
    # К сожалению, а АПИ ASO World багнут метод получения списка приложений - он вместо айдишника возвращает null.
    # По итогу невозможно сначала обновить список приложений, а затем для каждого из них обновить ключи.
    # Поэтому пришлось сначала получать все ключи. В них есть айдишник приложения, по которому можно уже получить инфу.

    logger.info("Updating apps and keywords data.")
    if not models.AppPlatform.objects.filter(name="Google").exists():
        logger.error("Can't find platform with name 'Google'!")
        return

    controller = ASOWorldAPIController()
    logger.info("Getting all keywords data.")
    keywords = controller.get_keywords()
    apps_cache = {}
    apps_cache: dict[str, models.App | None]

    for keyword_data in keywords:
        app_id = keyword_data['appId']
        if app_id not in apps_cache:
            app = models.App.objects.filter(package_id=app_id).first()

            if not app:
                app = __create_app_from_asoworld_by_package_id(
                    package_id=app_id, controller=controller)

            apps_cache[app_id] = app

        app = apps_cache[app_id]
        if not app:
            logger.warning(
                f"Can't find app with id {app_id} for keyword {keyword_data['word']}!")
            continue

        keyword_name = keyword_data['word']
        region_code = keyword_data['region']
        region = models.ASOWorldRegion.objects.filter(
            code=region_code).first()

        if not region:
            logger.warning(
                f"Can't find region {region_code} for keyword {keyword_name} and app with id {app.package_id}!")
            continue

        keyword = models.Keyword.objects.filter(
            name=keyword_name, region=region).first()

        if not keyword:
            keyword = models.Keyword(name=keyword_name, region=region)
            keyword.save()
            app.keywords.add(keyword)
            continue

        if not app.keywords.contains(keyword):
            app.keywords.add(keyword)

    logger.info("Updated!")


def __create_app_from_asoworld_by_package_id(package_id: str, controller: ASOWorldAPIController | None = None) -> models.App | None:
    """ Gets app from ASO World by given `package id` and creates it in database. 

    Args:
        package_id (str): package id which is app id in ASO World
        controller (ASOWorldAPIController | None, optional): If `None` creates new one. Defaults to None.

    Returns:
        `models.App`, if created, else `None`.
    """
    platform = models.AppPlatform.objects.filter(name="Google").first()
    if not platform:
        logger.error("Can't find platform with name 'Google'!")
        return None

    if not controller:
        controller = ASOWorldAPIController()

    logger.info(f"Getting info from ASO World for app with id {package_id}.")
    apps_list = controller.get_apps(appId=package_id)
    if len(apps_list) == 0:
        logger.warning(f"Can't find app in ASO World with id {package_id}.")
        return None

    app_data = apps_list[0]

    region = models.ASOWorldRegion.objects.filter(
        code=app_data['region']).first()

    if not region:
        logger.warning(
            f"Can't find region {app_data['region']} for app in ASO World with id {package_id}!")
        return None

    app = models.App(
        package_id=package_id,
        name=app_data['appName'],
        platform=platform,
        region=region,
        is_active=True,
        num=package_id,
        campaign_id=package_id,
    )
    app.save()

    logger.info(f"Created app with id {package_id} and name {app.name}.")
    return app


def update_orders():
    """ Updates orders in database """
    controller = ASOWorldAPIController()
    orders = controller.get_orders()

    for order_data in orders:
        order = models.ASOWorldOrder.objects.filter(
            asoworld_id=order_data['_id']).first()

        if not order:
            __create_order(data=order_data)
            continue

        __update_order(order=order, data=order_data)


def __update_order(order: models.ASOWorldOrder, data: dict[str, Any]):
    """Updates given ASO World order with given data

    Args:
        order (models.ASOWorldOrder): Order to update
        data (dict[str, Any]): data
    """
    logger.info(f"Updating order {order.asoworld_id}.")

    order.state = data['state']

    last_paused_at = __datetime_from_timestamp(
        data['lastPauseTime'] if 'lastPauseTime' in data else -1)
    order.last_paused_at = last_paused_at

    order.save()
    __update_order_data(order=order, data=data)


def __update_order_data(order: models.ASOWorldOrder, data: dict[str, Any]):
    """ Updates order's keywords data

    Args:
        order (models.ASOWorldOrder): order to update
        data (dict[str, Any]): new data
    """
    progress = data['progress']['words']
    region = data['region']
    for word in progress:
        __update_order_keywords_data(
            order=order,
            keyword_name=word,
            progress=progress,
            days=data['days'],
            region=region)


def __update_order_keywords_data(order: models.ASOWorldOrder,
                                 keyword_name: str,
                                 progress: dict[str, dict[str, int]],
                                 days: list[list[dict]],
                                 region: str):
    """ Updates order's keywords data

    Args:
        order (models.ASOWorldOrder): order to update
        keyword_name (str): keyword
        progress (dict[str, dict[str, int]]): current orders progress
        days (list[list[dict]]): daily data
        region (str): region code
    """
    keyword = order.app.keywords.filter(
        name=keyword_name,
        region=region
    ).first()

    if not keyword:
        logger.debug(
            f"No keyword {keyword}, connected for app {order.app.name}!")
        return

    date_to_update = datetime.now(tz=timezone.utc).date() - timedelta(days=1)

    old_data = models.ASOWorldOrderKeywordData.objects.filter(
        order=order,
        keyword=keyword
    )

    if old_data.count() == 0:
        __create_order_keyword_data(
            order=order,
            keyword_name=keyword_name,
            days=days,
            progress=progress,
            region=region
        )
        return

    data = models.ASOWorldOrderKeywordData.objects.filter(
        date=date_to_update,
        order=order,
        keyword=keyword
    ).first()

    if not data:
        data = models.ASOWorldOrderKeywordData(
            date=date_to_update,
            order=order,
            keyword=keyword
        )

    old_data_aggregated = old_data.aggregate(Sum("installs"))

    data.installs += old_data_aggregated['installs__sum']
    data.save()


def __create_order(data: dict[str, Any]) -> models.ASOWorldOrder | None:
    """ Creates ASO World order instance with given data

    Args:
        data (dict[str, Any]): data

    Returns:
        models.ASOWorldOrder: order instance
    """
    if data['platform'] != 1 or data['state'] in \
            [models.ASOWorldOrder.DRAFT, models.ASOWorldOrder.INVALID, models.ASOWorldOrder.PACKAGE]:
        logger.debug(
            f"Skipping. Platform {data['platform']}, state {data['state']}.")
        return

    logger.info(f"Creating order instance with id {data['_id']}.")
    app = models.App.objects.filter(package_id=data['appId']).first()
    if not app:
        logger.debug(f"No app found with package id {data['appId']}!")
        return

    started_at = __datetime_from_timestamp(data['startTime'])
    created_at = __datetime_from_timestamp(data['createTime'])
    if not started_at or not created_at:
        logger.debug(
            f"Start time or create time is not set for order with id {data['_id']}.")
        return

    order = models.ASOWorldOrder(
        asoworld_id=data['_id'],
        app=app,
        state=data['state'],
        submit_type=data['submitType'],
        install_type=data['installType'],
        price=data['orderPrice'],
        created_at=created_at,
        started_at=started_at,
        canceled_at=__datetime_from_timestamp(data['cancelTime']),
        finished_at=__datetime_from_timestamp(data['finishTime']),
        last_paused_at=__datetime_from_timestamp(
            data['lastPauseTime'] if 'lastPauseTime' in data else -1),
    )
    order.save()

    region = data['region']
    progress = data['progress']['words']
    for word in progress:
        __create_order_keyword_data(
            order=order,
            keyword_name=word,
            days=data['days'],
            progress=progress,
            region=region)
    return order


def __create_order_keyword_data(order: models.ASOWorldOrder,
                                keyword_name: str,
                                days: list[list[dict]],
                                progress: dict[str, dict[str, int]],
                                region: str):
    """ Creates order keyword daily data

    Args:
        order (models.ASOWorldOrder): order 
        keyword_name (str): keyword
        days (list[list[dict]]): daily data
        progress (dict[str, dict[str, int]]): progress for each keyword
        region (str): region code
    """
    logger.info(
        f"Creating order data instances for keyword [{region}] {keyword_name} for order with id {order.asoworld_id}.")
    if order.submit_type == models.ASOWorldOrder.PACKAGE:
        logger.debug(
            "Submit type of order is 'Package'. So its impossible to get keyword data!")
        return

    if not order.started_at:
        logger.warning(
            f"Order {order.asoworld_id} is not started yet!")
        return

    start_date = order.started_at.date()
    canceled_date = None if not order.canceled_at else order.canceled_at.date()
    finished_date = None if not order.finished_at else order.finished_at.date()

    if finished_date and not canceled_date:
        __create_finished_order_keyword_data(
            order=order, keyword_name=keyword_name, days=days, region=region)
        return

    keyword = order.app.keywords.filter(
        name=keyword_name,
        region=region
    ).first()

    if not keyword:
        logger.debug(
            f"No keyword {keyword}, connected for app {order.app.name}!")
        return

    current_date = datetime.now(tz=timezone.utc).date()
    kw_progress = {}

    for i, daily_data in enumerate(days):
        day = start_date + timedelta(days=i)

        if day > current_date or \
                (day == current_date and not canceled_date) or \
                (canceled_date and day > canceled_date):
            return

        keyword_data = list(
            filter(lambda x: x['word'] == keyword_name, daily_data))
        if len(keyword_data) == 0:
            return

        keyword_data = keyword_data[0]

        if not keyword.name in kw_progress:
            kw_progress[keyword.name] = 0

        installs = keyword_data['count']
        total_installs = progress[keyword.name]['finish']

        if installs + kw_progress[keyword.name] > total_installs:
            installs = total_installs - kw_progress[keyword.name]

        if installs == 0:
            continue

        kw_progress[keyword.name] += installs

        data = models.ASOWorldOrderKeywordData(
            order=order,
            keyword=keyword,
            installs=installs,
            date=day
        )
        data.save()


def __create_finished_order_keyword_data(order: models.ASOWorldOrder,
                                         keyword_name: str,
                                         days: list[list[dict]],
                                         region: str):
    """ Creates data in database if order was finished normally

    Args:
        order (models.ASOWorldOrder): order
        keyword_name (str): keyword
        days (list[list[dict]]): daily data
        region (str): region code
    """
    start_date = order.started_at.date()

    keyword = order.app.keywords.filter(
        name=keyword_name,
        region=region
    ).first()

    if not keyword:
        logger.debug(
            f"No keyword {keyword}, connected for app {order.app.name}!")
        return

    for i, daily_data in enumerate(days):
        day = start_date + timedelta(days=i)

        keyword_data = list(
            filter(lambda x: x['word'] == keyword_name, daily_data))

        if len(keyword_data) == 0:
            return
        keyword_data = keyword_data[0]

        data = models.ASOWorldOrderKeywordData(
            order=order,
            keyword=keyword,
            installs=keyword_data['count'],
            date=day
        )
        data.save()


def __datetime_from_timestamp(ts: int) -> datetime | None:
    return None if ts == -1 else datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
