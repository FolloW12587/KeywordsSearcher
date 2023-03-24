import logging
import os
import requests
from typing import Any, Callable


logger = logging.getLogger(__name__)


class ASOWorldAPIService:
    """ Class to connect to asoworld """
    PAGE_SIZE = 500

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

    @__apiMethod
    def app_list(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """ ASO World API method to get app's list from console with given `data`.

        Args:
            data (dict[str, Any]): Must have "pageSize" key in it.
                Optional can be "appName", "appId", "platform".

        Returns:
            bool: Is request succeded or not.
        """
        assert "pageSize" in data, "Incorrect data: pageSize must be set"

        endpoint = "App/list"
        headers = self.__getAuthorizationHeader()
        page = 0
        count = 1

        output = []
        while page * self.PAGE_SIZE < count:
            logger.info(f"Page {page}.")
            data['page'] = page
            r = requests.post(f"{self._host}/{endpoint}",
                              data=data, headers=headers)

            if r.status_code != 200:
                logger.error(
                    f"Getting app list from ASO World with data {data} ended with status code {r.status_code}. Message: {r.text}")
                return output

            response_data = r.json()
            if "P" not in response_data:
                logger.error(
                    f"Getting app list from ASO World with data {data} ended with status code {r.status_code} but haven't got 'P' in data. \
                        Message: {r.text}")
                return output

            count = response_data['P']['count']
            output += response_data['P']['list']
            page += 1

        logger.info(f"Got {len(output)} apps.")
        return output

    @__apiMethod
    def add_app(self, data: dict[str, Any]) -> bool:
        """ASO World API method to add app to console with given `data`.

        Args:
            data (dict[str, Any]): Must have "region", "appId" and "platform" keys in it.

        Returns:
            bool: Is request succeded or not.
        """
        assert "region" in data, "Incorrect data: region must be set"
        assert "appId" in data, "Incorrect data: appId must be set"
        assert "platform" in data, "Incorrect data: platform must be set"

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
    def keyword_list(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """ ASO World API method to get app's list from console with given `data`.

        Args:
            data (dict[str, Any]): Must have "pageSize" key in it.
                Optional can be "region", "appId", "platform", "word".

        Returns:
            bool: Is request succeded or not.
        """
        assert "pageSize" in data, "Incorrect data: pageSize must be set"

        endpoint = "Keyword/list"
        headers = self.__getAuthorizationHeader()
        page = 0
        count = 1

        output = []
        while page * self.PAGE_SIZE < count:
            logger.info(f"Page {page}.")
            data['page'] = page
            r = requests.post(f"{self._host}/{endpoint}",
                              data=data, headers=headers)

            if r.status_code != 200:
                logger.error(
                    f"Getting keyword list from ASO World with data {data} ended with status code {r.status_code}. Message: {r.text}")
                return output

            response_data = r.json()
            if "P" not in response_data:
                logger.error(
                    f"Getting keyword list from ASO World with data {data} ended with status code {r.status_code} but haven't got 'P' in data. \
                        Message: {r.text}")
                return output

            count = response_data['P']['count']
            output += response_data['P']['list']
            page += 1

        logger.info(f"Got {len(output)} keywords.")
        return output

    @__apiMethod
    def add_keyword(self, data: dict[str, Any]) -> bool:
        """ ASO World API method to add keyword to app

        Args:
            data (dict[str, Any]): Must have "region", "platform", "appId" and "keyword" keys in it.

        Returns:
            bool: True if succed
        """
        assert "region" in data, "Incorrect data: region must be set"
        assert "appId" in data, "Incorrect data: appId must be set"
        assert "platform" in data, "Incorrect data: platform must be set"
        assert "keyword" in data, "Incorrect data: keyword must be set"

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
    def order_list(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """ ASO World API method to get orders.

        Args:
            data (dict[str, Any]): Must have "pageSize" key. 
                Optional can be "orderId", "appId", "platform", "region", "state", "stime", "etime", "submitType".

        Returns:
            list[dict[str, Any]]: returns list of orders' data
        """
        assert "pageSize" in data, "Incorrect data: pageSize must be set"

        endpoint = "Order/list"
        headers = self.__getAuthorizationHeader()

        page = 0
        data_count = 1

        output = []
        while page * self.PAGE_SIZE < data_count:
            page += 1

            logger.info(f"Page {page}.")
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
