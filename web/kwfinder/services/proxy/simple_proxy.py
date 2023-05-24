import logging
import os
from time import sleep

from requests import Session
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3

def get_proxy() -> dict[str, str] | None:
    proxy = os.getenv("PROXY")
    if not proxy:
        logger.warning("Can't get proxy settings")
        return
    
    return {
        'http': proxy,
        'https': proxy
    }

def create_proxy_requests_session(proxy: dict[str, str], attempt: int = 1) -> Session | None:
    """Create requests session with given proxy. Max tries for creation is defined in `MAX_ATTEMPTS` variable.

    Args:
        proxy (dict[str, str]): given proxy in requests format
        attempt (int, optional): Current attempt num. Defaults to 1.

    Returns:
        Session | None: Created session. None if can't create session in `MAX_ATTEMPTS` tries or can't find test url.
    """
    logger.info(f"Creating requests session for proxy {safe_proxy_repr(proxy)}. Attempt {attempt}.")
    proxy_test_url = os.getenv('PROXY_TEST_URL')
    if not proxy_test_url:
        logger.warning("Can't find proxy_test_url for proxy to create working session.")
        return
    
    if attempt > MAX_ATTEMPTS:
        logger.error(f"Can't create working proxy session for proxy {safe_proxy_repr(proxy)} in {MAX_ATTEMPTS} tries!")
        return
    
    session = Session()
    session.proxies = proxy
    try:
        session.get(proxy_test_url)
    except ConnectionError:
        logger.warning(f"Connection error in creating session for proxy {safe_proxy_repr(proxy)} in attempt {attempt}.")
        sleep(2)
        return create_proxy_requests_session(proxy, attempt + 1)
    except Exception as e:
        logger.error(f"Unexpected error while creating session for proxy {safe_proxy_repr(proxy)}!")
        logger.exception(e)
        return
    
    return session


def safe_proxy_repr(proxies: dict[str, str]) -> str:
    if 'http' in proxies:
        proxy = proxies['http']

    elif 'https' in proxies:
        proxy = proxies['https']

    elif 'socks5' in proxies:
        proxy = proxies['socks5']

    else:
        logger.warning(f"Can't understand how to safe repr given proxy!")
        proxy = str(proxies)

    return proxy.split('@')[-1]