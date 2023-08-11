import json
import logging
from typing import Callable, Dict, Optional

import requests

from . import config

logger = logging.getLogger(__name__)


class TelegramBot:
    SAD_FACES_EMOJIS = config.SAD_FACE_EMOJIS

    def __init__(self) -> None:
        self._token = config.TELEGRAMBOT_TOKEN
        self._chat_id = config.TELEGRAMBOT_CHAT_ID
        self._host = 'https://api.telegram.org/bot'

    def __botMethod(f: Callable):  # type: ignore
        def wrapper(*args, **kwargs):
            logger.info(f"[TG Bot] {f.__name__} method is called!")
            return f(*args, **kwargs)
        return wrapper

    @__botMethod
    def sendMessage(self, message: str, *args, **kwargs) -> Optional[dict]:
        """ Method that sends message to telegram chat """
        method = "sendMessage"

        payload = {
            'text': message,
            'chat_id': self._chat_id,
            **kwargs
        }
        try:
            r = requests.post(self.__getUrlByMethodName(
                method), data=json.dumps(payload), headers=self.__getHeaders())

            if r.status_code != 200:
                logger.error(
                    f"Unexpected error while sending message: {r.text}")
                return
        except Exception as e:
            logger.exception(e)
            return

        return r.json()

    @__botMethod
    def sendDocument(self, path: str, *args, **kwargs) -> Optional[dict]:
        """ Method that sends document to telegram chat """
        method = "sendDocument"

        payload = {
            'chat_id': self._chat_id,
            **kwargs
        }

        try:
            with open(path, 'rb') as file:
                r = requests.post(self.__getUrlByMethodName(method=method),
                                  data=payload,
                                  files={"document": file})

                if r.status_code != 200:
                    logger.error(
                        f"Unexpected error while sending document: {r.text}")
                    return
        except Exception as e:
            logger.error(f"Can't send file {path}.")
            logger.exception(e)
            return

        return r.json()

    @__botMethod
    def getMe(self) -> Optional[dict]:
        """ A simple method for testing your bot's authentication token. """
        method = "getMe"
        try:
            r = requests.get(self.__getUrlByMethodName(
                method), headers=self.__getHeaders())
        except Exception as e:
            logger.exception(e)
            return

        return r.json()

    # def alertNewPayout(self, payout: models.Payout, partner_name: str, account_name: str) -> Optional[dict]:
    #     """ Alerts group about new `payout` """
    #     header = f"Зафиксирована новая заявка на выплату с аккаунта *{self.__translateMessage(account_name)}* в партнерке *{self.__translateMessage(partner_name)}*:\n```\n"
    #     data = [
    #         ["Сумма:", payout.amount],
    #         ["Валюта:", payout.currency],
    #         ["Дата:", payout.creation_date.strftime("%Y-%m-%d %H:%M:%S")],
    #         ["Реквизиты:", payout.payment_requisites],
    #         ["Статус:", payout.state],
    #         ["ID:", payout.id],
    #         ["ID в партнерке:", payout.in_partner_id],
    #     ]

    #     message = header + \
    #         self.__translateMessage(tabulate(data, tablefmt='plain')) + '```'
    #     return self.sendMessage(message, parse_mode='MarkdownV2')

    def __getHeaders(self, **kwargs) -> Dict[str, str]:
        return {
            "content-type": "application/json",
            **kwargs
        }

    def __getUrlByMethodName(self, method: str) -> str:
        return f"{self._host}{self._token}/{method}"

    @staticmethod
    def translateMessage(message: str) -> str:
        d = {
            '[': r'\[',
            ']': r'\]',
            '(': r'\(',
            ')': r'\)',
            '>': r'\>',
            '#': r'\#',
            '+': r'\+',
            '-': r'\-',
            '=': r'\=',
            '|': r'\|',
            '{': r'\{',
            '}': r'\}',
            '.': r'\.',
            '!': r'\!',
            '_': r'\_',
            '*': r'\*',
            '~': r'\~',
            '`': r'\`'
        }
        return message.translate(str.maketrans(d))
