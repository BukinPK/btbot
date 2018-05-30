import json
import os
from datetime import datetime, timedelta
from .config import ExcelConfig

basedir = os.path.abspath(os.path.dirname(__file__))+'/'


class Excel(ExcelConfig):

    def __init__(self, api):
        self._api = api

    def parser(self):
        if 'excel' in dir(self._api):
            result = self._api.excel.spreadsheets().values().get(
                spreadsheetId=self.LIST_ID, range=self.LIST_RANGE).execute()
            self.base = result.get('values', [])
        else:
            print('get api first')


class Data(ExcelConfig):

    _base = []

    def __init__(self, api):
        self._api = api
        self.excel = Excel(api)

    def __getitem__(self, key):
        return self._base[key]

    def __setitem__(self, key, val):
        self[key] = val

    def __repr__(self):
        return json.dumps(self._base, default=str, indent=4)

    def __call__(self):
        self.excel.parser()
        self.make_base()

    def make_base(self):
        link_map = {
            'twitter': 'https://twitter.com/',
            'facebook': 'https://www.facebook.com/',
            'telegram': 'https://t.me/'
            }
        self._base = []
        today = datetime.today()
        for excel_line in self.excel.base:
            base_line = {
                'id': 1,
                'social': [
                    {'name': 'twitter', 'limit': 5, 'link': 7},
                    {'name': 'facebook', 'limit': 6, 'link': 8},
                    {'name': 'telegram', 'limit': None, 'link': 9}
                    ],
                'week_start': 4,
                'social_data': {},
                'start': 0,
                'end': 0
                }
            try:
                base_line['id'] = excel_line[base_line['id']]
            except Exception:
                continue
            bad_link = []
            for social in base_line['social']:
                try:
                    social['link'] = excel_line[social['link']]
                    if social['link'] in ['', ' ']:
                        raise
                    social['link'] = social['link'].rstrip('/')
                    social['username'] = social['link'].split(
                        link_map[social['name']])[1]
                except Exception:
                    bad_link.append(social['name'])
                    continue
                else:
                    if social['limit']:
                        try:
                            social['limit'] = int(excel_line[social['limit']])
                        except Exception:
                            social['limit'] = None
                        else:
                            if social['limit'] is '':
                                social['limit'] = None
            for name in bad_link:
                for social in base_line['social']:
                    if name is social['name']:
                        base_line['social'].remove(social)
            if base_line['social'] == []:
                continue
            try:
                base_line['week_start'] = int(
                    excel_line[base_line['week_start']])
            except Exception:
                base_line['week_start'] = 0

            today_stamp = today.toordinal()
            i = 0
            while datetime.fromordinal(today_stamp-i).weekday() \
                    != base_line['week_start']:
                i += 1
            base_line['week_start'] = datetime.fromordinal(today_stamp-i)

            self._base.append(base_line)
