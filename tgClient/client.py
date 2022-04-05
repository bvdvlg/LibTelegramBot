from requests import Session
import helpers
from functools import partial

class TelegramClient:
    BASE_URL = "https://api.telegram.org"

    def init_session(self):
        self.session = Session()
        self.session.headers = {
            "charset": "UTF-8"
        }

    def __init__(self, token=None):
        if token:
            self.__token = token
        else:
            self.__token = helpers.obtain_key("telegram_token")
        self.session = None

        self.init_session()

    def patch(self, method, path, retries_num=1, **kwargs):
        http_codes = [429, 500, 502, 503, 504]
        request_url = "{}/bot{}/{}".format(self.BASE_URL, self.__token, path)
        response = getattr(self.session, method.lower())(request_url, files=kwargs)
        retries = 0
        while response.status_code in http_codes and retries < retries_num:
            response = getattr(self.session, method)(request_url, files=kwargs)
            retries += 1

        return response

    def __getattr__(self, item):
        return partial(self.patch, "GET", item)
