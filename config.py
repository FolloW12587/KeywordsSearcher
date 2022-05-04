import json


def __getSettingsData() -> dict:
    """ Returns dict data from settings.json """
    with open("settings.json", "r") as r:
        return json.loads(r.read())


URL = "https://play.google.com/store/search?q={keyword}&c=apps&hl=es-ES&gl=MX"
SETTINGS = __getSettingsData()

GOOGLE_PLAY_WINDOW_NUM = 0