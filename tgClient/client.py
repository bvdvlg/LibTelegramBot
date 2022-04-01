from requests import Session


class TelegramClient:
    BASE_URL = "https://api.telegram.org"

    def init_session(self):
        self.session = Session()
        self.session.headers = {
            "Content-Type": "multipart/form-data",
            "charset": "UTF-8"
        }

    def __init__(self, token):
        self.__token = token
        self.session = None

        self.init_session()

    def patch(self, method, path, **kwargs):
        http_codes = [429, 500, 502, 503, 504]
        request_url = "{}/bot{}/{}".format(self.BASE_URL, self.__token, path)
        response = getattr(self.session, method)(request_url)
        return response

    def __getattr__(self, item):
        return