import socks
import socket
from .login import Login, Api
from .poster import Poster
# from .parser import Parser
from .data import Data
from .config import SocksConfig

__all__ = ['Bot']
__author__ = 'BukinPK'
__version__ = '0.1'


class SocksEnabeler(SocksConfig):

    def __call__(self):
        if self.ENABLE:
            socks.set_default_proxy(self.TYPE, self.HOST, username=self.USER,
                                    password=self.PASS)
            socket.socket = socks.socksocket


class Bot:

    __all__ = [
        'api', 'login', 'data',
        'poster', 'enable_socks']

    socks = SocksEnabeler()
    api = Api()
    login = Login(Api)
    data = Data(api)
    poster = Poster(data)
    # parser = Parser(data)

    def __init__(self):
        pass
