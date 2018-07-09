class SocksConfig:
    '''
    Если хотите работать через соксы, прошу, вбивайте.
    Только пятые. На четвёртых не проверял.
    ENABLE = 1 для включения
    TYPE (выберите число, соответствующее типу используемого прокси):
        HTTP = 1
        SOCKS5 = 2
        SOCKS4 = 3
    '''
    ENABLE = 0
    TYPE = 2
    HOST = ''
    USER = ''
    PASS = ''


class ExcelConfig:
    '''
    Это лист екселя. ID можно скопировать из адресной строки.
    Следом идёт диапазон выборки для парсинга значений (вбит заранее).
    '''
    LIST_ID = ''
    LIST_RANGE = 'Лист1!A2:AB'


class GoogleConfig:
    '''
    Заходите на:
    https://console.developers.google.com/flows/enableapi?apiid=sheets.googleapis.com
    Создаёте приложение.
    Далее первое поле оставляете как есть (Googlr Sheets API),
    во втором выбераете CLI. И отмечаете "Данные пользователя".
    В следующем окне сбиваёте любую ебалу в обязательных полях.
    Главное чтоб url был валидный, а что там по нему - не важно.
    PROFIT
    После этого вам любезно предложат скачать учётные данные (client_id.json).
    Вы соглашайтесь и аккуратно кладите их в директорию /icobot/icobot/.
    PROFIT[2]
    '''
    pass


class TwitterConfig:
    '''
    https://apps.twitter.com/
    Создаёте приложение.
    Заходите во вкладку "Keys and Access Tokens".
    Берёте оттуда этих двух парней.
    '''
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''

    '''
    Далее в самом низу, на этой же вкладке, жмёте "Create my access token".
    Обновляете страницу и забираете оттуда следующих двух парней.
    '''
    ACCESS_TOKEN_KEY = ''
    ACCESS_TOKEN_SECRET = ''


class FacebookConfig:
    '''
    Эту хуйню пока пропускайте.
    GET TOKEN https://developers.facebook.com/tools/accesstoken
    '''
    TOKEN = ''


class TelegramConfig:
    pass


class ReportsConfig:
    '''
    Берём куки из браузера на БТТ
    '''
    _cookies = {
        'PHPSESSID': '',
        'SMFCookie129': '',
        '__cfduid': ''
        }
    _headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
        }
