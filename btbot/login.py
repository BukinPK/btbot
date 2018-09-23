import os
import shutil
from configparser import RawConfigParser as ConfigParser


__all__ = ['Api']


class Api:


    def __init__(self, conf=None):
        if isinstance(conf, str):
            self.get_config(conf)
        else:
            self.conf = conf
        self._api_names = {
            'twitter': self._twitter_login,
            'facebook': self._facebook_login,
            'telegram': self._telegram_login,
            'excel': self._excel_login,
            'btt': self._btt_login
            }
        
    def login(self, service:str=None):
        """service can be:
            'twitter', 'facebook', 'telegram' 'excel', 'btt'
            If service is None, autorisation will be on all services.
        """
        if not self.conf:
            print('get config first')
            return False

        if service: 
            if self.conf.has_section(service):
                self._api_names[service](dict(self.conf.items(service)))
            else:
                print(f'{service} has no config in config file')
        else:
            for name, service in self._api_names.items():
                if self.conf.has_section(name):
                    service(dict(self.conf.items(name)))
                else:
                    print(f'{name} has no config in config file')

    def proxy(self, conf):
        import socks, socket
        conf = dict(conf.items('proxy'))
        if int(conf['enable']):
            socks.set_default_proxy(
                proxy_type=conf['type'],
                addr=conf['host'],
                username=conf['user'],
                password=conf['paswd'])
            socket.socket = socks.socksocket
        else:
            socks.set_default_proxy()
            socket.socket = socks.socksocket

    def _twitter_login(self, conf):
        import twitter
        self.twitter = twitter.Api(
            consumer_key=conf['consumer_key'],
            consumer_secret=conf['consumer_secret'],
            access_token_key=conf['access_token_key'],
            access_token_secret=conf['access_token_secret'])

    def _facebook_login(self, conf):
        # import facebook
        # self._api.facebook = facebook.GraphAPI(
        #     access_token=conf.FACEBOOK_TOKEN)
        self.facebook = None

    def _telegram_login(self, conf):
        from telethon import TelegramClient
        from telethon.tl.functions.channels import JoinChannelRequest
        class TgApiWrapper:
            def __new__(cls):
                raise
            client = TelegramClient
            join = JoinChannelRequest
        self.telegram = TgApiWrapper

    def _excel_login(self, conf):
        import os
        from oauth2client import file, client, tools
        from apiclient.discovery import build
        from httplib2 import Http
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
        store = file.Storage(os.path.join('configs', 'credentials.json'))
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(
                os.path.join('configs', 'client_id.json'), SCOPES)
            creds = tools.run_flow(flow, store)
        self.excel = build('sheets', 'v4', http=creds.authorize(Http()))
        self.excel.LIST_ID = conf['list_id']
        self.excel.LIST_RANGE = conf['list_range']

    def _btt_login(self, conf):
        from btbot.bttapi import BttApi
        self.btt = BttApi(PHPSESSID=conf['phpsessid'],
                          SMFCookie129=conf['smfcookie129'],
                          cfduid=conf['__cfduid'])

    @classmethod
    def fromconfig(cls, path:str=None, dir='configs') -> list:
        if not path:
            fullpath = dir
            path = ''
        else:
            fullpath = os.path.join(dir, path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        conf = ConfigParser()

        if os.path.isdir(fullpath):
            api = []
            for file in os.listdir(fullpath):
                if os.path.isfile(os.path.join(fullpath, file)) and \
                        file.endswith('.conf'):
                    conf.read(os.path.join(fullpath, file))
                    api.append(cls(conf))
            if api:
                return api
            else:
                if path:
                    dir = os.path.join(dir, path)
                return cls.fromconfig(path='main.conf', dir=dir)

        if os.path.isfile(fullpath):
            conf.read(fullpath)
        else:
            if os.path.dirname(path):
                return cls.fromconfig(path=os.path.basename(path),
                    dir=os.path.join(dir, os.path.dirname(path)))
            if os.path.exists(fullpath):
                raise RuntimeError('is not dir, not file and not empty')
            basedir = os.path.abspath(os.path.dirname(__file__))
            shutil.copyfile(os.path.join(basedir, 'config.tpl'), fullpath)
            print(f'new config "{path}" are created in directory "{dir}"')
        return [cls(conf)]

    def get_config(self, path):
        if os.path.isfile(path):
            conf = ConfigParser()
            conf.read(path)
            self.conf = conf
        else:
            return None
