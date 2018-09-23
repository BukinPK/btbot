import requests
from lxml import html
import re
from datetime import datetime


__all__ = ['BttApi', 'Message']


class Message:
    
    _topic_xpath = 'tr/td/table/tr[1]/td[2]/a[3]'
    _board_xpath = 'tr/td/table/tr[1]/td[2]/a[2]'
    _text_xpath = 'tr/td/table/tr[2]/td/div'
    _date_xpath = 'tr/td/table/tr[1]/td[3]'
    _topic_reg = re.compile(r'topic=(\d+)')
    _date_reg = re.compile(
        r'on: (\w+ \d{2}, 20\d{2},|Today at) (\d{2}:\d{2}:\d{2}) (\w{2})')

    def __init__(self, post):
        self.post = post

    @property
    def date(self):
        date_arr = self._date_reg.findall(
            self.post.xpath(self._date_xpath)[0].text_content())[0]
        if date_arr[0] == 'Today at':
            date_str = datetime.strftime(datetime.today(), '%B %d, %Y,')
            date_str = f'{date_str} {date_arr[1]} {date_arr[2]}'
        else:
            date_str = f'{date_arr[0]} {date_arr[1]} {date_arr[2]}'
        return datetime.strptime(f'{date_str} +0000',
                                 '%B %d, %Y, %I:%M:%S %p %z')

    @property
    def topic_raw_link(self):
        return self.post.xpath(self._topic_xpath)[0].get('href')

    @property
    def topic_id(self):
        return self._topic_reg.findall(self.topic_raw_link)[0]

    @property
    def topic_link(self):
        return 'https://bitcointalk.org/index.php?topic=' + self.topic_id

    @property
    def text(self):
        return [x for x in self.post.xpath(self._text_xpath)[0].itertext()]

    @property
    def board_name(self):
        return self.post.xpath(self._board_xpath)[0].text

    @property
    def board_link(self):
        return self.post.xpath(self._board_xpath)[0].get('href')

    @property
    def subject(self):
        return self.post.xpath(self._topic_xpath)[0].text


class BttApi:

    profile_link = 'https://bitcointalk.org/index.php?action=profile'
    _headers = {'User-Agent': ''.join(('Mozilla/5.0 (X11; Linux x86_64) Apple',
                                       'WebKit/537.36 (KHTML, like Gecko) Chr',
                                       'ome/67.0.3396.79 Safari/537.36'))}

    def __init__(self, PHPSESSID=None, SMFCookie129=None, cfduid=None):
        self._cookies = dict(PHPSESSID=PHPSESSID, SMFCookie129=SMFCookie129,
                             __cfduid=cfduid)
        self.s = requests.Session()
        self.s.cookies.update(self._cookies)
        self.s.headers.update(self._headers)

    def get_messages(self, postpage=0):
        posts_xpath = '//*[@id="bodyarea"]/table/tr/td[1]/table/tr[2]/td/a[2]'
        posts_selector = '//*[@id="bodyarea"]/table/tr/td[2]'
        r = self.s.get(self.profile_link)
        self.posts_link = html.fromstring(r.text).xpath(posts_xpath)[0].attrib['href']
        r = self.s.get(self.posts_link)

        raw_table = html.fromstring(r.text).xpath(posts_selector)[0]
        raw_posts = raw_table.getchildren()[1:-1]
        listing_sector = raw_table.getchildren()[-1]

        posts = []
        for post in raw_posts:
            posts.append(Message(post))
        return posts
        # проверить

    def _get_post_page(self, link:str):
        postpage_xpath = '//*[@id="quickModForm"]/table[2]' + \
                         '/tr/td[2]/table/tr/td[2]/a[1]'
        r = self.s.get(link)
        postpage_link = html.fromstring(r.text).xpath(postpage_xpath)[0].attrib['href']
        return self.s.get(postpage_link)

    # уточнить тип post_page
    def _get_payload(self, post_page:requests.Response, form_num=1) -> dict:
        parsed = html.fromstring(post_page.text)
        inputs = dict(parsed.forms[form_num].inputs)
        payload = dict()
        for key in inputs:
            payload[key] = inputs[key].value
        payload['ns'] = 'NS'
        del payload['preview']
        del payload['post']
        return payload

    def send_message(self, link:str, msg:str, sub=None) -> bool:
        if not msg and not isinstance(msg, str):
            return False
        post_xpath = '//*[@id="postmodify"]'
        post_page = self._get_post_page(link)
        payload = self._get_payload(post_page)
        payload['message'] = msg
        if sub:
            payload['subject'] = sub
        post_link = html.fromstring(post_page.text).xpath(
            post_xpath)[0].attrib['action']
        send_result = self.s.post(post_link, data=payload)
        # сделать проверку send_result
        
