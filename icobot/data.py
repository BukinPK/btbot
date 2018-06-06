import json
import os
from datetime import datetime, timedelta
from .config import ExcelConfig


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


class Data:

    _base = []
    link_allow = {
        'twitter': ['https://twitter.com/'],
        'facebook': ['https://www.facebook.com/'],
        'telegram': ['https://t.me/', 'https://web.telegram.org/']
        }

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

    def link_checker(self, link, name):
        for allowed_link in self.link_allow[name]:
            if allowed_link in link:
                return link.strip('/ ')

    def get_username(self, link, name):
        for allowed_link in self.link_allow[name]:
            try:
                username = link.split(allowed_link)[1]
            except IndexError:
                continue
            else:
                return username

    def make_base(self):
        self._base = []
        today = datetime.today()
        for excel_line in self.excel.base:
            base_line = {
                'id': 1,
                'social': {
                    'twitter': {'limit': 5, 'link': 7},
                    'facebook': {'limit': 6, 'link': 8},
                    'telegram': {'limit': None, 'link': 9}
                    },
                'week_start': 4,
                'start': 2,
                'end': 3
                }

            try:
                base_line['id'] = excel_line[base_line['id']]
            except Exception:
                continue

            bad_link = []
            for s_name, social in base_line['social'].items():
                # link and username define
                try:
                    social['link'] = excel_line[social['link']]
                    social['link'] = self.link_checker(social['link'], s_name)
                    if not social['link']:
                        raise
                    social['username'] = self.get_username(
                        social['link'], s_name)
                    if not social['username']:
                        raise
                except Exception:
                    bad_link.append(s_name)
                    continue
                # define limit
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
                del base_line['social'][name]

            if base_line['social'] == {}:
                continue

            # week_start add
            try:
                base_line['week_start'] = int(
                    excel_line[base_line['week_start']])
            except Exception:
                base_line['week_start'] = 0

            # week_start compute last week
            today_stamp = today.toordinal()
            i = 0
            while datetime.fromordinal(today_stamp-i).weekday() \
                    != base_line['week_start']:
                i += 1
            base_line['week_start'] = datetime.fromordinal(today_stamp-i)

            # start/end date add
            try:
                base_line['start'] = datetime.strptime(
                    excel_line[base_line['start']].strip(), '%d.%m.%Y')
            except ValueError:
                base_line['start'] = None
            try:
                base_line['end'] = datetime.strptime(
                    excel_line[base_line['end']].strip(), '%d.%m.%Y')
            except ValueError:
                base_line['end'] = None

            # add line to base
            self._base.append(base_line)
