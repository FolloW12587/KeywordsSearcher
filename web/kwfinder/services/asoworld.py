import logging
import os
import requests
from typing import Any, Callable

from web.kwfinder import models


logger = logging.getLogger(__name__)


class ASOWorldAPIService:
    """ Class to connect to asoworld """

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

    def __getAuthorizationHeader(self) -> dict[str, str]:
        """ Returns request authorization header """
        return {"Authorization": f"Bearer {self._token}"}
