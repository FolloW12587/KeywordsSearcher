from typing import Any

from web.kwfinder import models
from web.kwfinder.services.asoworld import ASOWorldAPIService


class ASOWorldAPIController:
    def __init__(self) -> None:
        self._service = ASOWorldAPIService()

    def add_app(self, app: models.App) -> bool:
        """ Adds `app` to ASO World

        Args:
            app (App): App to add to ASO World

        Returns:
            bool: Is app added successfully or not
        """
        data = {
            "region": app.region.code,
            "appId": app.package_id,
            "platform": app.platform.asoworld_id
        }
        return self._service.add_app(data)

    def add_keyword(self, app: models.App, keyword: models.Keyword) -> bool:
        """ Adds `models.Keyword` to ASO World app, that is connected to `models.App`.

        Args:
            app (models.App): App to add keyword to
            keyword (models.Keyword): keyword to add

        Returns:
            bool: True if success
        """
        data = {
            "region": keyword.region.code,
            "appId": app.package_id,
            "platform": app.platform.asoworld_id,
            "keyword": keyword.name
        }
        return self._service.add_keyword(data)

    def get_orders(self, app: models.App | None = None) -> list[dict[str, Any]]:
        """ Gets list of orders in ASO World

        Args:
            app (models.App | None): App to get orders for. If None, returns all orders.

        Returns:
            list[dict[str, Any]]: List of orders
        """
        data: dict[str, Any]
        data = {
            "pageSize": ASOWorldAPIService.PAGE_SIZE,
            "platform": 1
        }

        if app:
            data["platform"] = app.platform.asoworld_id
            data["appId"] = app.package_id

        return self._service.order_list(data)

    def get_keywords(self, app: models.App | None = None,
                     keyword: models.Keyword | None = None,
                     region: models.ASOWorldRegion | None = None,
                     appId: str | None = None,
                     word: str | None = None,
                     region_code: str | None = None,
                     platform: int | None = None) -> list[dict[str, Any]]:
        """ Gets list of keywords in ASO World

        Args:
            app (models.App | None, optional): Filters keywords by given `app`. Defaults to None.
            keyword (models.Keyword | None, optional): Filters keywords by given `keyword`. Defaults to None.
            region (models.ASOWorldRegion | None, optional): Filters keywords by given `region`. Defaults to None.
            appId (str | None, optional): Filters keywords by app id. Defaults to None.
            word (str | None, optional): Filters keywords by word. Defaults to None.
            region_code (str | None, optional): Filters keywords by region code. Defaults to None.
            platform (int | None, optional): Filters keywords by platform. Defaults to None.

        Returns:
            list[dict[str, Any]]: List of keywords' info
        """
        data: dict[str, Any]
        data = {
            "pageSize": ASOWorldAPIService.PAGE_SIZE,
            "platform": 1
        }

        if app:
            data["platform"] = app.platform.asoworld_id
            data["appId"] = app.package_id
        else:
            if appId:
                data["appId"] = appId

            if platform:
                data["platform"] = platform

        if region:
            data['region'] = region.code
        elif region_code:
            data['region'] = region_code

        if keyword:
            data['word'] = keyword.name
        elif word:
            data['word'] = word

        return self._service.keyword_list(data)

    def get_apps(self, app: models.App | None = None,
                 appId: str | None = None,
                 appName: str | None = None,
                 platform: int | None = None) -> list[dict[str, Any]]:
        """ Gets list of apps in ASO World

        Args:
            app (models.App | None, optional): Filters apps by `app`. Defaults to None.
            appId (str | None, optional): Filters apps by app id. Defaults to None.
            appName (str | None, optional): Filters apps by app name. Defaults to None.
            platform (int | None, optional): Filters apps by platform. Defaults to None.

        Returns:
            list[dict[str, Any]]: List of apps' info
        """
        data: dict[str, Any]
        data = {
            "pageSize": ASOWorldAPIService.PAGE_SIZE,
            "platform": 1
        }

        if app:
            data["platform"] = app.platform.asoworld_id
            data["appId"] = app.package_id
        else:
            if appId:
                data["appId"] = appId

            if appName:
                data["appName"] = appId

            if platform:
                data["platform"] = platform

        return self._service.app_list(data)
