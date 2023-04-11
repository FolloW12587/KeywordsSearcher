import json
import logging
import os
from datetime import date
from typing import Any, Callable

import requests

from web.kwfinder import models

logger = logging.getLogger(__name__)


class KeitaroAPIService:
    """Class to connect to keitaro admin"""

    def __init__(self) -> None:
        assert os.getenv("KEITARO_API_KEY"), "KEITARO_API_KEY environment variable is not set!"
        assert os.getenv("KEITARO_HOST"), "KEITARO_HOST environment variable is not set!"
        self._api_key = os.getenv("KEITARO_API_KEY", "")
        self._host = os.getenv("KEITARO_HOST", "") + "/admin_api/v1"

    @staticmethod
    def __apiMethod(f: Callable):
        def wrapper(*args, **kwargs):
            logger.info(f"[Keitaro] {f.__name__} method is called!")
            return f(*args, **kwargs)

        return wrapper

    def getReport(self, campaign_id_list: list[str], date_from: date, date_to: date) -> list[dict]:
        """Gets statistics from keitaro of campaigns with its `campaign_ids`
        in date period from `date_from` to `date_to`.

        Args:
            campaign_id_list ([str]): list of ids of keitaro campaigns
            date_from (date): start of the period
            date_to (date): end of the period

        Returns:
            list[dict]: results
        """
        logger.info(
            f"Creating request body for keitaro report for campaigns {campaign_id_list}, \
                    for period from {date_from}, to {date_to}."
        )
        data = {
            "range": {"from": date_from.strftime(r"%Y-%m-%d"), "to": date_to.strftime(r"%Y-%m-%d"), "timezone": "UTC"},
            "columns": [],
            "metrics": [
                models.KeitaroDailyAppData.UNIQUE_USERS_COUNT_FIELD_NAME,
                models.KeitaroDailyAppData.CONVERSIONS_COUNT_FIELD_NAME,
                models.KeitaroDailyAppData.SALES_COUNT_FIELD_NAME,
                models.KeitaroDailyAppData.REVENUE_FIELD_NAME,
            ],
            "grouping": [models.KeitaroDailyAppData.DATE_FIELD_NAME, models.KeitaroDailyAppData.CAMPAIGN_ID_FIELD_NAME],
            "filters": [
                {
                    "name": models.KeitaroDailyAppData.CAMPAIGN_ID_FIELD_NAME,
                    "operator": "IN_LIST",
                    "expression": campaign_id_list,
                }
            ],
            "sort": [
                {"name": models.KeitaroDailyAppData.CAMPAIGN_ID_FIELD_NAME, "order": "asc"},
                {"name": models.KeitaroDailyAppData.DATE_FIELD_NAME, "order": "asc"},
            ],
            "summary": True,
        }

        logger.debug(f"Body generated: {data}.")
        return self.__buildReport(data)

    @__apiMethod
    def __buildReport(self, data: dict[str, Any]) -> list[dict]:
        """Gets report from keitaro with given `data`

        Args:
            data (dict): body of request

        Returns:
            list[dict]: rows
        """
        endpoint = "/report/build"
        headers = self.__getAuthorizationHeader()

        total = 1
        offset = 0
        limit = 100

        rows = []

        while offset < total:
            logger.info(f"Sending. Total: {total}, Offset: {offset}.")

            data["limit"] = limit
            data["offset"] = offset

            r = requests.post(f"{self._host}{endpoint}", data=json.dumps(data), headers=headers)

            if r.status_code != 200:
                logger.error(f"Request to {endpoint} ended with {r.status_code} code: {r.text}")
                return rows

            results = r.json()

            if "total" not in results or "rows" not in results:
                logger.error(
                    f"Request to {endpoint} ended with {r.status_code} code but has no expected parameters: {results}"
                )
                return rows

            total = results["total"]
            offset += limit

            rows += results["rows"]

        return rows

    def __getAuthorizationHeader(self) -> dict[str, str]:
        """Returns request authorization header"""
        return {"Api-Key": self._api_key}
