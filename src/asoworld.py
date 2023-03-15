from datetime import datetime, timedelta, timezone
from django.db.models import Sum
import logging
import os
from typing import Any

from web.kwfinder import models
from web.kwfinder.services.asoworld import ASOWorldAPIService


logger = logging.getLogger(__name__)


def upload_regions():
    """ Uploads regions from `resources/regions.csv` to ASOWorldRegion table """
    path = "resources/regions.csv"

    if not os.path.isfile(path):
        logger.error(f"File {path} doesn't exist!")
        return

    with open(path, 'r') as regions_file:
        for line in regions_file:
            region = models.ASOWorldRegion.objects.filter(
                code=line.split(";")[0]
            ).first()

            if region:
                continue

            region = models.ASOWorldRegion(*line.split(";"))
            region.is_app_store_supported = region.is_app_store_supported == 'true'
            region.is_google_play_supported = region.is_google_play_supported == 'true'
            region.save()

    logger.info("Uploaded.")


def update_orders():
    """ Updates orders in database """
    service = ASOWorldAPIService()
    orders = service.getOrders()

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

    match order.state, data['state']:
        case models.ASOWorldOrder.ACCOUNTING, models.ASOWorldOrder.CANCELED:
            order.state = data['state']
            return
        case models.ASOWorldOrder.PAUSED, \
                models.ASOWorldOrder.CANCELED | models.ASOWorldOrder.PAUSED | models.ASOWorldOrder.ACCOUNTING:
            last_paused_at = __datetime_from_timestamp(data['lastPauseTime'])
            if order.last_paused_at == last_paused_at:
                order.state = data['state']
                return
            __update_order_data(order=order, data=data)
        case models.ASOWorldOrder.PAUSED | models.ASOWorldOrder.ACTIVE, _:
            __update_order_data(order=order, data=data)
        case state1, state2 if state1 == state2:
            return
        case _:
            logger.warning(
                f"Unexpected state change from {order.state} to {data['state']}")

    order.state = data['state']
    order.save()


def __update_order_data(order: models.ASOWorldOrder, data: dict[str, Any]):
    """ Updates orders last paused time and keywords data

    Args:
        order (models.ASOWorldOrder): order to update
        data (dict[str, Any]): new data
    """
    last_paused_at = __datetime_from_timestamp(
        data['lastPauseTime'] if 'lastPauseTime' in data else -1)
    order.last_paused_at = last_paused_at
    order.save()

    __update_order_keywords_data(
        order, progress=data['progress']['words'])


def __update_order_keywords_data(order: models.ASOWorldOrder, progress: dict[str, dict[str, int]]):
    """ Updates order's keywords data

    Args:
        order (models.ASOWorldOrder): order to update
        progress (dict[str, dict[str, int]]): current orders progress
    """
    date_to_update = datetime.now(tz=timezone.utc).date() - timedelta(days=1)

    for keyword_name in progress:
        keyword = models.Keyword.objects.filter(
            name=keyword_name,
            app_type=order.app.app_type
        ).first()

        if not keyword:
            logger.warning(
                f"No keyword {keyword_name} for app {order.app.name}!")
            continue

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

        old_data = models.ASOWorldOrderKeywordData.objects.filter(
            order=order,
            keyword=keyword
        ).aggregate(Sum("installs"))
        old_data['installs__sum'] = 0 if old_data['installs__sum'] == None \
            else old_data['installs__sum']

        data.installs += old_data['installs__sum']
        data.save()


def __create_order(data: dict[str, Any]) -> models.ASOWorldOrder | None:
    """ Creates ASO World order instance with given data

    Args:
        data (dict[str, Any]): data

    Returns:
        models.ASOWorldOrder: order instance
    """
    if data['platform'] != 1 or data['state'] in \
            [models.ASOWorldOrder.DRAFT, models.ASOWorldOrder.ACCOUNTING, models.ASOWorldOrder.INVALID]:
        # logger.info(f"Skipping. Platform {data['platform']}, state {data['state']}.")
        return

    logger.info(f"Creating order instance with id {data['_id']}.")
    app = models.App.objects.filter(package_id=data['appId']).first()
    if not app:
        logger.warning(f"No app found with package id {data['appId']}!")
        return

    started_at = __datetime_from_timestamp(data['startTime'])
    created_at = __datetime_from_timestamp(data['createTime'])
    if not started_at or not created_at:
        logger.warning(
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

    __create_order_keyword_data(
        order, days=data['days'], progress=data['progress']['words'])
    return order


def __create_order_keyword_data(order: models.ASOWorldOrder, days: list[list[dict]], progress: dict[str, dict[str, int]]):
    """ Creates order keyword daily data

    Args:
        order (models.ASOWorldOrder): order 
        days (list[list[dict]]): daily data
        progress (dict[str, dict[str, int]]): progress for each keyword
    """
    logger.info(
        f"Creating order keyword data instances for order with id {order.asoworld_id}.")
    if order.submit_type == models.ASOWorldOrder.PACKAGE:
        logger.warning(
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
        __create_finished_order_keyword_data(order=order, days=days)
        return

    current_date = datetime.now(tz=timezone.utc).date()
    kw_progress = {}

    for i, daily_data in enumerate(days):
        day = start_date + timedelta(days=i)

        if day > current_date or \
                (day == current_date and not canceled_date) or \
                (canceled_date and day > canceled_date):
            return

        for keyword_data in daily_data:
            keyword = models.Keyword.objects.filter(
                name=keyword_data['word'],
                app_type=order.app.app_type
            ).first()

            if not keyword:
                if i == 0:
                    logger.warning(
                        f"Cannot find keyword {keyword_data['word']} for app {order.app.name}.")
                continue

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


def __create_finished_order_keyword_data(order: models.ASOWorldOrder, days: list[list[dict]]):
    """ Creates data in database if order was finished normally

    Args:
        order (models.ASOWorldOrder): order
        days (list[list[dict]]): daily data
    """
    start_date = order.started_at.date()

    for i, daily_data in enumerate(days):
        day = start_date + timedelta(days=i)

        for keyword_data in daily_data:
            keyword = models.Keyword.objects.filter(
                name=keyword_data['word'],
                app_type=order.app.app_type
            ).first()

            if not keyword:
                if i == 0:
                    logger.warning(
                        f"Cannot find keyword {keyword_data['word']} for app {order.app.name}.")
                continue

            data = models.ASOWorldOrderKeywordData(
                order=order,
                keyword=keyword,
                installs=keyword_data['count'],
                date=day
            )
            data.save()


def __datetime_from_timestamp(ts: int) -> datetime | None:
    return None if ts == -1 else datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
