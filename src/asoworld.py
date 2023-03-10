from datetime import datetime, timedelta, timezone
from django.db.models import F
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

    for order in orders:
        db_order = models.ASOWorldOrder.objects.filter(
            asoworld_id=order['_id']).first()

        if not db_order:
            __create_order(data=order)
            continue

        __update_order(order=db_order, data=order)


def __update_order(order: models.ASOWorldOrder, data: dict[str, Any]):
    """Updates given ASO World order with given data

    Args:
        order (models.ASOWorldOrder): Order to update
        data (dict[str, Any]): data
    """
    logger.info(f"Updating order {order.asoworld_id}.")
    match data['state']:
        case models.ASOWorldOrder.PAUSED:
            __encrease_paused_dates(order)
        case models.ASOWorldOrder.ACTIVE as new_state:
            if order.state == new_state:
                return
            __new_state_active(order)
        case models.ASOWorldOrder.COMPLETED as new_state:
            if order.state == new_state:
                return
            __new_state_complete(order)
        case models.ASOWorldOrder.CANCELED | models.ASOWorldOrder.INVALID \
                | models.ASOWorldOrder.ACCOUNTING as new_state:
            if order.state == new_state:
                return
            __new_state_canceled(order)
        case _:
            logger.warning(
                f"Invalid state change from {order.state} to {data['state']}.")

    order.state = data['state']
    order.save()


def __encrease_paused_dates(order: models.ASOWorldOrder):
    current_date = datetime.now(tz=timezone.utc).date()

    keywords_data = models.ASOWorldOrderKeywordData.objects.filter(
        order=order,
        state=models.ASOWorldOrderKeywordData.WAITING
    )

    if len(keywords_data) > 0:
        earliest_date = keywords_data.earliest('date').date
        if earliest_date < current_date:
            keywords_data.update(
                date=F('date') + (current_date - earliest_date))


def __new_state_active(order: models.ASOWorldOrder):
    current_date = datetime.now(tz=timezone.utc).date()
    models.ASOWorldOrderKeywordData.objects.filter(
        order=order,
        state=models.ASOWorldOrderKeywordData.WAITING,
        date__lt=current_date
    ).update(state=models.ASOWorldOrderKeywordData.DONE)


def __new_state_complete(order: models.ASOWorldOrder):
    models.ASOWorldOrderKeywordData.objects.filter(
        order=order,
        state=models.ASOWorldOrderKeywordData.WAITING
    ).update(state=models.ASOWorldOrderKeywordData.DONE)


def __new_state_canceled(order: models.ASOWorldOrder):
    models.ASOWorldOrderKeywordData.objects.filter(
        order=order,
        state=models.ASOWorldOrderKeywordData.WAITING
    ).update(state=models.ASOWorldOrderKeywordData.CANCELED)


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
        order_price=data['orderPrice'],
        created_at=created_at,
        started_at=started_at,
        canceled_at=__datetime_from_timestamp(data['cancelTime']),
        finished_at=__datetime_from_timestamp(data['finishTime']),
    )
    order.save()

    __create_order_keyword_data(order, days=data['days'])
    return order


def __create_order_keyword_data(order: models.ASOWorldOrder, days: list[list[dict]]):
    """ Creates order keyword daily data

    Args:
        order (models.ASOWorldOrder): order 
        days (list[list[dict]]): daily data
    """
    logger.info(
        f"Creating order keyword data instances for order with id {order.asoworld_id}.")
    if order.submit_type == models.ASOWorldOrder.PACKAGE:
        logger.warning(
            "Submit type of order is 'Package'. So its impossible to get keyword data!")
        return

    current_date = datetime.now(tz=timezone.utc).date()
    start_date = None if not order.started_at else order.started_at.date()
    canceled_date = None if not order.canceled_at else order.canceled_at.date()

    for i, daily_data in enumerate(days):
        if start_date == None:
            for keyword_data in daily_data:
                keyword = models.Keyword.objects.filter(
                    name=keyword_data['word'],
                    app_type=order.app.app_type
                ).first()

                if not keyword:
                    logger.info(
                        f"Cannot find keyword {keyword_data['word']} for app {order.app.name}.")
                    continue

                data = models.ASOWorldOrderKeywordData(
                    order=order,
                    keyword=keyword,
                    installs=keyword_data['count'],
                    state=models.ASOWorldOrderKeywordData.WAITING if canceled_date == None
                    else models.ASOWorldOrderKeywordData.CANCELED
                )
                data.save()

            continue

        day = start_date + timedelta(days=i)

        state = models.ASOWorldOrderKeywordData.DONE
        if day >= current_date:
            state = models.ASOWorldOrderKeywordData.WAITING

        if canceled_date and day >= canceled_date:
            state = models.ASOWorldOrderKeywordData.CANCELED

        for keyword_data in daily_data:
            keyword = models.Keyword.objects.filter(
                name=keyword_data['word'],
                app_type=order.app.app_type
            ).first()

            if not keyword:
                logger.info(
                    f"Cannot find keyword {keyword_data['word']} for app {order.app.name}.")
                continue

            data = models.ASOWorldOrderKeywordData(
                order=order,
                keyword=keyword,
                installs=keyword_data['count'],
                state=state,
                date=day
            )
            data.save()


def __datetime_from_timestamp(ts: int) -> datetime | None:
    return None if ts == -1 else datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
