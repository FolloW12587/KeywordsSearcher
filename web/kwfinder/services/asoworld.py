import logging
import os
import requests
from typing import Any, Callable

from web.kwfinder import models


logger = logging.getLogger(__name__)


class ASOWorldAPIService:
    """ Class to connect to asoworld """
    PAGE_SIZE = 1000

    def __init__(self) -> None:
        assert os.getenv("ASOWORLD_TOKEN"),\
            "ASOWORLD_TOKEN environment variable is not set!"
        assert os.getenv("ASOWORLD_HOST"),\
            "ASOWORLD_HOST environment variable is not set!"
        self._token = os.getenv("ASOWORLD_TOKEN", "")
        self._host = os.getenv("ASOWORLD_HOST", "") + "/openApi"

    @staticmethod
    def __apiMethod(f: Callable):
        def wrapper(*args, **kwargs):
            logger.info(f"[ASOWorld] {f.__name__} method is called!")
            return f(*args, **kwargs)
        return wrapper

    def add_app(self, app: models.App) -> bool:
        """ Adds `app` to ASO World

        Args:
            app (App): App to add to ASO World

        Returns:
            bool: Is app added successfully or not
        """
        data = {
            "region": app.app_type.asoworld_region.code,
            "appId": app.package_id,
            "platform": app.platform.asoworld_id
        }
        return self.__add_app(data)

    def add_keyword(self, app: models.App, keyword: str) -> bool:
        """ Adds `keyword` to ASO World app, that is connected to `models.App`.

        Args:
            app (models.App): App to add keyword to
            keyword (str): keyword to add

        Returns:
            bool: True if success
        """
        data = {
            "region": app.app_type.asoworld_region.code,
            "appId": app.package_id,
            "platform": app.platform.asoworld_id,
            "keyword": keyword
        }
        return self.__add_keyword(data)

    def getOrders(self, app: models.App | None = None) -> list[dict[str, Any]]:
        """ Gets list of orders in ASO World

        Args:
            app (models.App | None): App to get orders for. If None, returns all orders.

        Returns:
            list[dict[str, Any]]: List of orders
        """
        data: dict[str, Any]
        data = {
            "page": 1,
            "pageSize": self.PAGE_SIZE
        }

        if app:
            data["platform"] = app.platform.asoworld_id
            data["appId"] = app.package_id
            data["region"] = app.app_type.asoworld_region.code

        return self.__order_list(data)

    @__apiMethod
    def __add_app(self, data: dict[str, Any]) -> bool:
        """ASO World API method to add app to console with given `data`.

        Args:
            data (dict[str, Any]): Must have "region", "appId" and "platform" keys in it.

        Returns:
            bool: Is request succeded or not.
        """
        endpoint = "App/add"
        headers = self.__getAuthorizationHeader()
        r = requests.post(f"{self._host}/{endpoint}",
                          data=data, headers=headers)

        if r.status_code != 200:
            logger.error(
                f"Adding app to ASO World with data {data} ended with status code {r.status_code}. Message: {r.text}")
            return False

        return True

    @__apiMethod
    def __add_keyword(self, data: dict[str, Any]) -> bool:
        """ ASO World API method to add keyword to app

        Args:
            data (dict[str, Any]): Must have "region", "platform", "appId" and "keyword" keys in it.

        Returns:
            bool: True if succed
        """
        endpoint = "Keyword/add"
        headers = self.__getAuthorizationHeader()
        r = requests.post(f"{self._host}/{endpoint}",
                          data=data, headers=headers)

        if r.status_code != 200:
            logger.error(
                f"Adding keyword to app in ASO World with data {data} ended with status code {r.status_code}. Message: {r.text}")
            return False

        return True

    @__apiMethod
    def __order_list(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """ ASO World API method to get orders.

        Args:
            data (dict[str, Any]): Must have "pageSize" key. 
                Optional can be "orderId", "appId", "platform", "region", "state", "stime", "etime", "submitType".

        Returns:
            list[dict[str, Any]]: returns list of orders' data
        """
        endpoint = "Order/list"
        headers = self.__getAuthorizationHeader()

        page = 0
        data_count = 1

        output = []
        while page * self.PAGE_SIZE < data_count:
            page += 1

            data['page'] = page

            r = requests.post(f"{self._host}/{endpoint}",
                              data=data, headers=headers)

            if r.status_code != 200:
                logger.error(
                    f"Getting orders list from ASO World with data {data} ended with status code {r.status_code}. Message: {r.text}")
                return output

            response_data = r.json()
            if "P" not in response_data:
                logger.error(
                    f"Getting orders list from ASO World with data {data} ended with status code {r.status_code} but haven't got 'P' in data. \
                        Message: {r.text}")
                return output

            response_data = response_data['P']
            data_count = response_data['count']
            output += response_data['list']

        logger.info(f"Got {len(output)} orders.")
        return output

    def __getAuthorizationHeader(self) -> dict[str, str]:
        """ Returns request authorization header """
        return {"Authorization": f"Bearer {self._token}"}
