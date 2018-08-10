import sys
from abc import ABC
from datetime import datetime, timedelta, time
from time import sleep
from random import randint, choice, shuffle
import re


__all__ = ['Bounty', 'Twitter', 'Facebook', 'Telegram']


class Social(ABC):

    wait = 60
    _sep = ('.', ')', ' -')

    def __init__(self, api, link, week_limit=None, week_start=None):
        self.api = api.__dict__.get(self.__class__.__name__.lower())
        self.link = link
        self._week_start_raw = week_start
        self.week_limit = week_limit
        self.followed = None
        self.check_link()

    def __repr__(self):
        return f'{type(self).__name__}({self.username})'

    @staticmethod
    def start():
        pass

    @property
    def week_start(self) -> datetime:
        return compute_last_week(self._week_start_raw)

    @property
    def dict(self):
        return dict(link=self.link, week_limit=self.week_limit)

    def get_data(self, arr=False, rand=0):
        return None

    def check_link(self):
        if not self.link:
            self.username = None
            return False
        for link in self.service_links:
            link_reg = re.compile(rf'^{link}/(\w*)[/]?$')
            username = link_reg.findall(self.link)
            if username:
                self.username = username[0]
                return True
        self.username = None
        return False

class Twitter(Social):

    day_limit = 3
    hour_limit = 1
    wait = 60
    service_links = ('https://twitter.com',)

    def get_data(self, arr=False, rand=0):
        '''get data for last week'''
        posts = []
        for post in self._get_posts(week=1):
            posts.append('%s/%s/status/%s' % (self.service_links[0],
                                              post.user.screen_name,
                                              post.id_str))
        if not posts:
            return None
        if arr:
            return posts
        message = 'Twitter (like + retweet):'
        for i, post in enumerate(posts, start=1):
            message += f'\n{i}{self._sep[rand]} {post}'
        return message

    def start(self):

        week_posted = self._get_posts(week=1)
        ico_week_posts = self._get_posts(target=True, week=1)
        if ico_week_posts is False:
            print('LINK ERROR', self.link)
            return False
        week_can_post = self._cut_posted(ico_week_posts, week_posted)
        if not week_can_post:
            print('No posts for this week')
            return False

        if self.week_limit and len(week_posted) >= self.week_limit:
            print('week limit is exceeded')
            return False
        week_posts_allow = self.week_limit - len(week_posted)

        day_posted = self._get_posts(posts_given=week_posted, day=1)
        if len(day_posted) >= self.day_limit:
            print('day limit is exceeded')
            return False
        day_posts_allow = self.day_limit - len(day_posted)

        hour_posted = self._get_posts(posts_given=day_posted, hour=1)
        if len(hour_posted) >= self.hour_limit:
            print('hour limit is exceeded')
            return False
        hour_posts_allow = self.hour_limit - len(hour_posted)

        for num in range(1, hour_posts_allow+1):
            if num <= day_posts_allow:
                if not self.week_limit or num <= week_posts_allow:
                    try:
                        if not self.followed and not self.api.LookupFriendship(
                                screen_name=self.username)[0].following:
                            self.api.CreateFriendship(
                                screen_name=self.username)
                            self.followed = True
                            print('friend add')
                            sleep(randint(1, 3))
                        if not week_can_post[-num].favorited:
                            self.api.CreateFavorite(week_can_post[-num])
                            sleep(randint(1, 3))
                        self.api.PostRetweet(week_can_post[-num].id)
                    except Exception as ex:
                        print(ex)
        return True

    def _cut_posted(self, posts_given, posted):
        return_posts = []
        for post in posts_given:
            for my_post in posted:
                for status in (my_post.quoted_status,
                               my_post.retweeted_status):
                    if status and status.id == post.id:
                        break
                else:
                    continue
                break
            else:
                return_posts.append(post)
        return return_posts

    def _get_posts(self, target=None, posts_given=None, day=0, week=0, hour=0):
        if target:
            target = self.username
        return_posts = []
        today = datetime.today()
        if week:
            day = (today - self.week_start).days
            week = 0
        max_id = None
        while True:
            if posts_given:
                posts = posts_given
            else:
                try:
                    posts = self.api.GetUserTimeline(
                        screen_name=target, max_id=max_id)
                except Exception:
                    return False
            if posts == []:
                return return_posts
            for post in posts:
                if datetime.fromtimestamp(post.created_at_in_seconds) > \
                        today-timedelta(weeks=week, days=day, hours=hour):
                    if not target:
                        for status in [post.quoted_status,
                                       post.retweeted_status]:
                            if status and status.user.screen_name == \
                                    self.username:
                                return_posts.append(post)
                                if not posts_given and not post.favorited:
                                    self.api.CreateFavorite(post)
                                    print('[tw like]', self.link)
                                    sleep(randint(1, 3))
                    else:
                        return_posts.append(post)
                else:
                    return return_posts
            if posts_given:
                return return_posts
            max_id = posts[-1].id-1


class Telegram(Social):

    service_links = ('https://t.me', 'https://web.telegram.org')

    def start(self):
        sys.exit(0)


class Facebook(Social):

    service_links = ('https://www.facebook.com',)

    def start(self):
        sys.exit(0)


class Bounty:

    social_names = {
        'twitter': Twitter,
        'facebook': Facebook,
        'telegram': Telegram
        }
    _date_formats = ('%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d')
    _id_reg = re.compile(r'topic=(\d+)')

    def __init__(self, api, report_link, week_start=None, start=None, end=None):

        self.report_link = report_link
        self.api = api
        self._week_start_raw = week_start
        self.start = start
        self.end = end
        self.socials = dict()

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.socials.items())[key]
        else:
            return self.socials[key]

    def __repr__(self):
        return 'Bounty(week_start=%s, start=%s, end=%s, %s)' % (
            self._week_start_raw, self._date(self.start),
            self._date(self.end), list(self.socials.values()))

    @property
    def id(self):
        if not self.report_link:
            return None
        id = self._id_reg.findall(self.report_link)
        if id:
            return id[0]

    def add_social(self, social:str, link:str, week_limit:int=None):
        self.socials.update({
            social: self.social_names[social](
                api=self.api, link=link, week_limit=week_limit,
                week_start=self._week_start_raw)
            })

    @property
    def week_start(self) -> datetime:
        return compute_last_week(self._week_start_raw)
        
    def _date(self, time):
        if isinstance(time, datetime):
            return str(time.date())
    
    def check_links(self, wipe=False) -> dict:
        '''run method check_link() in every social, returns dict of socials'''
        checked = dict()
        for key, social in self.socials.items():
            if social.check_link():
                checked.update({key: social})
        if wipe:
            self.socials = checked
        return checked
    
    @property
    def is_actual_date(self) -> bool:
        '''return True if bounty not out of date'''
        today = datetime.today()
        if self.start and self.start.date() > today.date():
            return False
        if self.end and self.end.date() <= today.date():
            return False
        return True
    
    @property
    def is_report_time(self) -> bool:
        '''report_date is week_start - 1'''
        if not self.is_actual_date:
            return False
        today = datetime.today()
        if today.weekday() == (self.week_start - timedelta(days=1)).weekday() \
                and today.hour > 16:
            return True
        else:
            return False
        
    @property
    def is_report_need(self) -> bool:
        if not self.id or not self.is_report_time:
            return False
        today = datetime.today()
        i = 0
        while True:
            messages = self.api.btt.get_messages(postpage=i)
            for msg in messages:
                if msg.date > datetime.combine(today.date(),
                                               time(16)).astimezone():
                    if msg.topic_id == self.id:
                        return False
                    else:
                        continue
                else:
                    return True
            return True  # вместо пагинации
            i += 1

    @property
    def dict(self):
        return dict(start=self._date(self.start), end=self._date(self.end),
                    report_link=self.report_link,
                    week_start=self._week_start_raw,
                    socials=list(self.socials.values()))

    def call_socials(self):
        for social in self.socials.values():
            social.start()

    def send_report(self) -> bool:
        message = self.get_data()
        return self.api.btt.send_message(self.report_link, message)

    def get_data(self, arr=False):
        data = []
        rand = randint(0, 2)
        for social in self.socials.values():
            social_data = social.get_data(arr=arr, rand=rand)
            if social_data:
                data.append(social_data)
        if not data:
            return None
        if arr:
            return data
        shuffle(data)
        date_format = choice(self._date_formats)
        date = 'Week: ' + ' - '.join((
            str(self.week_start.strftime(date_format)),
            str(datetime.today().strftime(date_format))))
        data.insert(0, date)
        data = '\n\n'.join(data)
        return data


def compute_last_week(week_day=None):
    if week_day is None:
        week_day = 0
    today_stamp = datetime.today().toordinal()
    i = 0
    while datetime.fromordinal(today_stamp-i).weekday() != week_day:
        i += 1
    return datetime.fromordinal(today_stamp-i)
