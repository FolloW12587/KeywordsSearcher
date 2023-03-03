import logging
import os
from typing import Callable


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

    def __getAuthorizationHeader(self) -> dict[str, str]:
        """ Returns request authorization header """
        return {"Authorization": f"Bearer {self._token}"}
