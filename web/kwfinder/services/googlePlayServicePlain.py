import logging
from typing import List
from urllib.parse import urljoin

# from django.conf import settings
import requests
from bs4 import BeautifulSoup

from web.kwfinder.services.proxy.mobile_proxy import MobileProxy

logger = logging.getLogger(__name__)


class GooglePlayService:
    """ Class to manage google store service """

    def __init__(self, base_url: str, thread_num: int = 0, proxy: MobileProxy | None = None) -> None:
        self.base_url = base_url
        self.thread_num = thread_num
        self.proxy=proxy

    def getAllAppLinks(self, keyword: str, attributes: str) -> List[str]:
        """ Retruns list of all apps' links from store page with given attributes. """
        l = []
        url = f"{self.base_url}&q={keyword}&{attributes}"

        proxies = None if not self.proxy or not self.proxy.proxy_info else self.proxy.proxy_info.proxies_dict

        r = requests.get(url, proxies=proxies)

        parsed_html = BeautifulSoup(r.text, features="html.parser")
        main = parsed_html.find('a', class_='Qfxief')
        if main:
            l.append(urljoin(url, main['href']))

        apps = parsed_html.find_all('a', class_='Gy4nib')
        return l + [urljoin(url, x['href']) for x in apps]
