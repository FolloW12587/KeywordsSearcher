import logging
import os
from datetime import datetime, timedelta
from time import sleep
from typing import Callable

import requests

from .dataclasses import ProxyInfo

logger = logging.getLogger(__name__)


class MobileProxy:
    IP_CHANGE_TIMEOUT = timedelta(minutes=2)
    EQUIPMENT_CHANGE_TIMEOUT = timedelta(minutes=10)

    def __init__(self) -> None:
        assert os.getenv("PROXY_API_KEY"), "PROXY_API_KEY environment variable is not set!"
        assert os.getenv("PROXY_API_HOST"), "PROXY_API_HOST environment variable is not set!"
        assert os.getenv("PROXY_ID"), "PROXY_ID environment variable is not set!"
        self._api_key = os.getenv("PROXY_API_KEY", "")
        self._host = os.getenv("PROXY_API_HOST", "")
        self._proxy_id = os.getenv("PROXY_ID", "")

        self.last_time_ip_changed = datetime.now()
        self.last_time_equipment_changed = datetime.now()

        self.proxy_info = self.getProxyInfo()

    @property
    def __authorizationHeader(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}
    
    @property
    def requests_proxies_dict(self) -> dict[str, str] | None:
        return self.proxy_info.proxies_dict if self.proxy_info else None
    
    @staticmethod
    def __apiMethod(f: Callable):
        def wrapper(*args, **kwargs):
            logger.info(f"[MobileProxy] {f.__name__} method is called!")
            return f(*args, **kwargs)
        return wrapper
    
    @__apiMethod
    def getProxyInfo(self) -> ProxyInfo | None:
        """ Gets proxy info

        Returns:
            ProxyInfo: proxy data
        """
        command = "get_my_proxy"

        url = f"{self._host}?command={command}&proxy_id={self._proxy_id}"
        r = requests.get(url, headers=self.__authorizationHeader)

        if r.status_code != 200:
            logger.error(f"Error while getting info about proxy with id {self._proxy_id}. Message: {r.text}.")
            return
        
        if not r.json():
            logger.error(f"Can't find info about proxy with id {self._proxy_id}.")
            return
        
        return ProxyInfo(**r.json()[0])

    @__apiMethod
    def rotateProxyIp(self) -> bool:
        """Rotates current proxy ip"""
        if self.proxy_info == None:
            logger.warning("No proxy to rotate")
            return False
        
        time_since_last_change = datetime.now() - self.last_time_ip_changed
        if time_since_last_change < self.IP_CHANGE_TIMEOUT:
            logger.info(f"Too little time since last ip change {time_since_last_change}. Sleeping.")
            sleep(time_since_last_change.total_seconds())
        
        user_agent = "Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.102011-10-16 20:23:10"
        headers = {"User-Agent": user_agent}
        
        url = self.proxy_info.proxy_change_ip_url
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            logger.error(f"Error while rotating ip if proxy with id {self._proxy_id}. Message: {r.text}.")
            return False

        self.last_time_ip_changed = datetime.now()
        self.proxy_info = self.getProxyInfo()

        return True