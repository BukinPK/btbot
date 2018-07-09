import socks
import socket
from .login import Login, Api
from .poster import Poster
from .data import Data
from .config import SocksConfig
from .reports import Reports

__all__ = ['Bot']
__author__ = 'BukinPK'
__email__ = 'bukinpk@gmail.com'
__version__ = '0.2'
__description__ = 'Bot for BOUNTY parser and register'
__license__ = 'GPL'
__url__ = 'https://github.com/BukinPK/icobot'


class ProxyEnabeler(SocksConfig):

    def __call__(self):
        if self.ENABLE:
            socks.set_default_proxy(self.TYPE, self.HOST, username=self.USER,
                                    password=self.PASS)
            socket.socket = socks.socksocket


class Bot:

    __all__ = ['api', 'login', 'data', 'poster', 'proxy']

    proxy = ProxyEnabeler()
    api = Api()
    login = Login(api)
    data = Data(api)
    poster = Poster(data)
    reports = Reports(data)
