import os
from oauth2client import file, client, tools
from apiclient.discovery import build
from httplib2 import Http
from .config import TwitterConfig, FacebookConfig, TelegramConfig

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    def __init__(self, api):
        self._api = api


class Twitter(Config, TwitterConfig):

    def __call__(self):
        import twitter
        self._api.twitter = twitter.Api(
            consumer_key=self.CONSUMER_KEY,
            consumer_secret=self.CONSUMER_SECRET,
            access_token_key=self.ACCESS_TOKEN_KEY,
            access_token_secret=self.ACCESS_TOKEN_SECRET)


class Facebook(Config, FacebookConfig):

    def __call__(self):
        # import facebook
        # self._api.facebook = facebook.GraphAPI(access_token=FACEBOOK_TOKEN)
        self._api.facebook = None


class Telegram(Config, TelegramConfig):

    def __call__(self):
        self._api.telegram = None


class Login:

    def __init__(self, api):
        self._api = api
        self.twitter = Twitter(api)
        self.facebook = Facebook(api)
        self.telegram = Telegram(api)

    def __call__(self):
        for social in [self.excel, self.twitter,
                       self.facebook, self.telegram]:
            social()

    def excel(self):
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
        store = file.Storage(os.path.join(basedir, 'credentials.json'))
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(
                os.path.join(basedir, 'client_id.json'), SCOPES)
            creds = tools.run_flow(flow, store)
        self._api.excel = build('sheets', 'v4', http=creds.authorize(Http()))


class Api:
    pass
