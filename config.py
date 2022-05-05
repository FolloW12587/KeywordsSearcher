from distutils.debug import DEBUG
import json
from datetime import datetime


def __getSettingsData() -> dict:
    """ Returns dict data from settings.json """
    with open("settings.json", "r") as r:
        return json.loads(r.read())


URL = "https://play.google.com/store/search?q={keyword}&c=apps&hl=es-ES&gl=MX"
CURRENT_DATETIME_STR = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
CURRENT_DATE_STR = datetime.now().strftime("%Y-%m-%d")

DEBUG = False

# getting settings from settings.json
_SETTINGS = __getSettingsData()
assert "keyword" in _SETTINGS, "keyword must be specified in settings.json"
assert "driver_path" in _SETTINGS, "driver_path must be specified in settings.json"
assert "keyword_file_path" in _SETTINGS, "keyword_file_path must be specified in settings.json"
assert "time_to_sleep" in _SETTINGS, "time_to_sleep must be specified in settings.json"
assert "app_links" in _SETTINGS, "app_links list must be specified in settings.json"
assert "is_headless_mode" in _SETTINGS, "is_headless_mode must be specified in settings.json"
assert "number_of_threads" in _SETTINGS, "number_of_threads must be specified in settings.json"


KEYWORD = _SETTINGS['keyword']
DRIVER_PATH = _SETTINGS['driver_path']
KEYWORD_FILE_PATH = _SETTINGS['keyword_file_path']
TIME_TO_SLEEP = _SETTINGS['time_to_sleep']
APP_LINKS = _SETTINGS['app_links']
IS_HEADLESS_MODE = _SETTINGS['is_headless_mode']
NUMBER_OF_THREADS = _SETTINGS['number_of_threads']
