import requests
import webbrowser
from lxml import html
import json
from .config import ReportsConfig


class Reports:

    def __init__(self, data):
        self._data = data
        self.links = []
        self._reports = []

    def parse(self):
        for line in self._data:
            self.links.append(line['id'])
            self._reports.append(Report(line['id'], line['week_start']))

    def __call__(self):
        for report in self:
            report()

    def __getitem__(self, key):
        return self._reports[key]

    def __setitem__(self, key, val):
        self[key] = val

    def __repr__(self):
        return json.dumps(self._reports, default=str, indent=4)


class Report(ReportsConfig):

    s = requests.Session()
    home_link = 'https://bitcointalk.org'
    profile_link = 'https://bitcointalk.org/index.php?action=profile'

    def __init__(self, link=None, report_date=None):
        self.link = link
        self.report_date = report_date
        self.msg = None
        self.sub = None
        self.s.cookies.update(self._cookies)
        self.s.headers.update(self._headers)

    def __call__(self):
        if self.isReportDay and self.reportNeed:
            self.makeMessage()
            getPostPage()
            getPayload()
            self.sendReport()

    def makeMessage(self):
        self.msg = None

    def getLastReportDate(self):
        pass

    @property
    def isReportDay(self):
        today = datetime.date()
        if today == self.report_dste:
            return True

    @property
    def reportNeed(self):
        pass

    def getPosts(self, postpage=0):
        posts_xpath = '//*[@id="bodyarea"]/table/tr/td[1]/table/tr[2]/td/a[2]'
        posts_selector = '//*[@id="bodyarea"]/table/tr/td[2]'

        r = self.s.get(self.profile_link)
        self.posts_link = html.fromstring(r.text).xpath(posts_xpath)[0].attrib['href']

        r = self.s.get(self.posts_link)
        self.posts_table = html.fromstring(r.text).xpath(posts_selector)[0]

    def getPayload(form_num=1):
        parsed = html.fromstring(self.post_page.text)
        inputs = dict(parsed.forms[form_num].inputs)
        payload = {}
        for key in inputs:
            payload[key] = inputs[key].value
        payload['ns'] = 'NS'
        del payload['preview']
        del payload['post']
        payload['message'] = self.msg
        if self.sub is not None:
            payload['subject'] = self.sub
        self.payload = payload

    def getPostPage(self):
        postpage_xpath = '//*[@id="quickModForm"]/table[2]/tr/td[2]/table/tr/td[2]/a[1]'
        post_xpath = '//*[@id="postmodify"]'

        r = self.s.get(self.link)
        postpage_link = html.fromstring(r.text).xpath(postpage_xpath)[0].attrib['href']

        self.post_page = s.get(postpage_link)

    def sendReport(self):
        self.getPayload()
        post_link = html.fromstring(self.post_page.text).xpath(
            post_xpath)[0].attrib['action']
        self.send_result = self.s.post(post_link, data=self.payload)

    def responseOpen(self, r=None):
        if not r:
            r = self.send_result
        with open('r.html', 'w') as f:
            f.write(self.r.text)
        webbrowser.open('r.html')
