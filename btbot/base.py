import json
import os
from datetime import datetime, timedelta
from multiprocessing import Process
from threading import Thread
from time import sleep
from random import randint
from .bounty import Bounty


__all__ = ['BountyBase']


class BountyBase:


    def __init__(self, api):
        self.api = api
        self.arr = []

    def __getitem__(self, key):
        return self.arr[key]

    def __repr__(self):
        lenght = len(self.arr)
        checked = len(self.check(wipe=False))
        bad = lenght - checked
        return 'BountyBase(len=%s, good=%s, bad=%s)' % (lenght, checked, bad)

    def report(self, cycle=True, background=True):
        if background:
            print('repors started')
            self.report_thread = Thread(target=self.report,
                                      kwargs={'background':False})
            self.report_thread.start()
        else:
            while True:
                for bounty in self.arr:
                    if bounty.is_report_need:
                        bounty.send_report()
                        wait = randint(300, 600)
                        print(f'[sleep: {wait}] report: {bounty}')
                        sleep(wait)
                    else:
                        print('not report need:', bounty)
                        sleep(randint(5, 10))
                if cycle is False:
                    return True

    def stop_report(self):
        self.report_thread.terminate()
        self.report_thread.join()
        self.report_thread = None
        
    def start(self, cycle=True, social=None):
        if not social:
            self.threads = dict()
            for key in Bounty.social_names.keys():
                self.threads.update({key: Thread(target=self.start,
                                                  kwargs={'social': key,
                                                          'cycle': cycle})})
                self.threads[key].start()
            return None
        else:
            while True:
                for bounty in self.arr:
                    if social in bounty.socials.keys():
                        print(bounty[social])
                        result = bounty[social].start()
                        if result:
                            wait = randint(abs(bounty[social].wait / 2),
                                           abs(bounty[social].wait * 1.5))
                            print(f'[action for {bounty[social]}] [wait: {wait}]')
                            sleep(wait)
                        else:
                            sleep(randint(1, 3))
                if cycle is False:
                    print('[end of the', social, 'cycle]')
                    return True
                else:
                    print('[end of the %s cycle] [wait %s]' % (
                        social, Bounty.social_names[social].wait))
                    sleep(Bounty.social_names[social].wait)
                    print('[new', social, 'cycle]')

    def stop(self, social=None):
        if social:
            self.threads[social].terminate()
            self.threads[social].join()
            del self.threads[social]
        else:
            for key, social in self.threads.items():
                social.terminate()
                social.join()
            self.threads = []

    def check(self, wipe=True, date=True, links=True):
        checked = []
        for bounty in self.arr:
            if date:
                check_date = bounty.is_actual_date
            else:
                check_date = True
            if links:
                checked_links = bounty.check_links(wipe=wipe)
            else:
                checked_links = True
            if check_date and checked_links:
                checked.append(bounty)
        if wipe:
            self.arr = checked
            return None
        return checked

    @property
    def dict(self):
        temp_dict = []
        for bounty in self.arr:
            temp_dict.append(bounty.dict)
        return temp_dict

    def make(self, type='full'):
        self.raw = self.api.excel.spreadsheets().values().get(
            spreadsheetId=self.api.excel.LIST_ID,
            range=self.api.excel.LIST_RANGE).execute().get('values', [])
        if type is 'raw':
            return self.raw
        if type is 'dict':
            self.dict = []
        self.arr = []

        def get_field(num, inst=str, blank=None):
            try:
                if raw[num]:
                    return inst(raw[num]) 
                else:
                    return blank
            except (IndexError, ValueError, TypeError):
                return blank

        for raw in self.raw:
            bounty_params = {
                'report_link': 1,
                'start': 2,
                'end': 3,
                'week_start': 4
                }
            social_params = {
                'twitter': {'week_limit': 5, 'link': 7},
                'facebook': {'week_limit': 6, 'link': 8},
                'telegram': {'week_limit': None, 'link': 9}
                }

            # id
            bounty_params['report_link'] = get_field(
                bounty_params['report_link'])
            # week_start add
            bounty_params['week_start'] = get_field(
                bounty_params['week_start'], int)
            # start date
            bounty_params['start'] = get_field(bounty_params['start'])
            if bounty_params['start']:
                try:
                    bounty_params['start'] = datetime.strptime(
                        bounty_params['start'].strip(), '%d.%m.%Y')
                except ValueError:
                    bounty_params['start'] = None
            # end date
            bounty_params['end'] = get_field(bounty_params['end'])
            if bounty_params['end']:
                try:
                    bounty_params['end'] = datetime.strptime(
                        bounty_params['end'].strip(), '%d.%m.%Y')
                except ValueError:
                    bounty_params['end'] = None
            # socials add
            for social, params in social_params.items():
                # link 
                params['link'] = get_field(params['link'])
                # limit
                params['week_limit'] = get_field(params['week_limit'], int)

            # make dict
            if type is 'dict':
                bounty_dict = bounty_params.copy()
                bounty_dict.update({'social_params': social_params})
                self.dict_debug.append(bounty_dict)
                continue

            # Bounty add
            bounty = Bounty(self.api, **bounty_params)
            for social, params in social_params.items():
                bounty.add_social(social, **params)
            self.arr.append(bounty)
