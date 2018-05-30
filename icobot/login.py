import os
from oauth2client import file, client, tools
from apiclient.discovery import build
from httplib2 import Http
from .config import TwitterConfig

basedir = os.path.abspath(os.path.dirname(__file__))+'/'


class Twitter(TwitterConfig):

    def __init__(self, api):
        self._api = api

    def __call__(self):
        import twitter
        self._api.twitter = twitter.Api(
            consumer_key=self.CONSUMER_KEY,
            consumer_secret=self.CONSUMER_SECRET,
            access_token_key=self.ACCESS_TOKEN_KEY,
            access_token_secret=self.ACCESS_TOKEN_SECRET)


class Login:

    def __init__(self, api):
        self._api = api
        self.twitter = Twitter(api)

    def __call__(self):
        for social in [self.excel, self.twitter,
                       self.facebook, self.telegram]:
            social()

    def excel(self):
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
        store = file.Storage(basedir+'credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(basedir+'client_id.json',
                                                  SCOPES)
            creds = tools.run_flow(flow, store)
        self._api.excel = build('sheets', 'v4', http=creds.authorize(Http()))

    def facebook(self):
        # import facebook
        # self._api.facebook = facebook.GraphAPI(access_token=FACEBOOK_TOKEN)
        self._api.facebook = None

    def telegram(self):
        self._api.telegram = None


class Api:
    pass