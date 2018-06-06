import sys
from datetime import datetime, timedelta
from random import randint
from time import sleep
from threading import Thread, Lock


class Call:

    name = 'unnamed social network'
    wait_after_once = 60

    def __init__(self, data):
        self._data = data
        self._api = data._api
        self.lock = Lock()

    def __call__(self):
        self.call_cycle()

    def _call_all(self):
        today = datetime.today()
        for line in self._data:
            if self.name not in line['social']:
                continue
            social = line['social'][self.name]
            if line['start'] and line['start'].date() > today.date():
                print('[bounty even not start yet]', social['link'])
                continue
            if line['end'] and line['end'].date() <= today.date():
                print('[expire date of bounty]', social['link'])
                continue
            social['week_start'] = line['week_start']
            print('[try]', social['link'])
            status = self._call(social)
            del social['week_start']
            if status:
                print('[post & wait]', social['link'])
                sleep(randint(40, 80))

    def _call(self, social):
        print('[no backend for ', self.name, '] EXIT', sep='')
        sys.exit(1)

    def call_once(self):
        if not self.lock.locked():
            self.lock.acquire()
        self._call_all()
        print('[end of the list]')
        if self.lock.locked():
            self.lock.release()

    def call_cycle(self):
        print('[cycle start for ', self.name, ']', sep='')
        while True:
            self.call_once()
            print('[wait', self.wait_after_once, 'seconds]')
            sleep(self.wait_after_once)


class Twitter(Call):

    name = 'twitter'
    day_limit = 3
    hour_limit = 1

    def _call(self, social):

        week_posted = self.get_posts(social, 'my_wall', week=1)
        ico_week_posts = self.get_posts(social, 'ico_wall', week=1)
        if ico_week_posts is False:
            print('[AAAAAAAAAAAAAAAAAaaaaaaaA!ugh!!!!!11au1!!!11!stopit!!!!!]',
                  social['link'])
            return False
        week_can_post = self.cut_posted(ico_week_posts, week_posted)

        if social['limit'] and len(week_posted) >= social['limit']:
            return False
        week_posts_allow = social['limit'] - len(week_posted)

        day_posted = self.get_posts(
            social, 'my_wall', posts_given=week_posted, day=1)
        if len(day_posted) >= self.day_limit:
            return False
        day_posts_allow = self.day_limit - len(day_posted)

        hour_posted = self.get_posts(
            social, 'my_wall', posts_given=day_posted, hour=1)
        if len(hour_posted) >= self.hour_limit:
            return False
        hour_posts_allow = self.hour_limit - len(hour_posted)

        if week_can_post:
            for num in range(hour_posts_allow):
                if num+1 <= day_posts_allow:
                    if not social['limit'] or num+1 <= week_posts_allow:
                        week_can_post.reverse()
                        try:
                            if not week_can_post[num].favorited:
                                self._api.twitter.CreateFavorite(
                                    week_can_post[num])
                                sleep(randint(1, 3))
                            self._api.twitter.PostRetweet(
                                week_can_post[num].id)
                        except Exception:
                            return False
                        finally:
                            week_can_post.reverse()
                        return True
        return False

    def cut_posted(self, posts_given, posted):
        return_posts = []
        for post in posts_given:
            for my_post in posted:
                for status in [
                        my_post.quoted_status, my_post.retweeted_status]:
                    if status and status.id == post.id:
                        continue
            return_posts.append(post)
        return return_posts

    def get_posts(self, social, target, posts_given=None,
                  day=0, week=0, hour=0):
        if target not in ['my_wall', 'ico_wall']:
            raise
        if target is 'ico_wall':
            target = social['username']
        else:
            target = None
        return_posts = []
        today = datetime.today()
        if week:
            day = (today - social['week_start']).days
            week = 0
        max_id = None
        while True:
            if posts_given:
                posts = posts_given
            else:
                try:
                    posts = self._api.twitter.GetUserTimeline(
                        screen_name=target, max_id=max_id)
                except Exception:
                    return False
            if posts == []:
                return return_posts
            for post in posts:
                if datetime.fromtimestamp(post.created_at_in_seconds) > \
                        today-timedelta(weeks=week, days=day, hours=hour):
                    if not target:  # FOR MY_WALL
                        for status in [post.quoted_status,
                                       post.retweeted_status]:
                            if status and status.user.screen_name == \
                                    social['username']:
                                return_posts.append(post)
                                if not posts_given and not post.favorited:
                                    self._api.twitter.CreateFavorite(post)
                                    print('[tw like]', social['link'])
                                    sleep(randint(1, 3))
                    else:  # FOR TARGET
                        return_posts.append(post)
                else:
                    return return_posts
            if posts_given:
                return return_posts
            max_id = posts[-1].id-1


class Facebook(Call):

    name = 'facebook'


class Telegram(Call):

    name = 'telegram'


class Poster:

    def __init__(self, data):
        self.twitter = Twitter(data)
        self.facebook = Facebook(data)
        self.telegram = Telegram(data)

    def __getitem__(self, key):
        return [self.twitter, self.facebook, self.telegram][key]

    def __call__(self):
        self.call_cycle()

    def call_once(self):
        for social in self:
            Thread(target=social.call_once).start()

    def call_cycle(self):
        for social in self:
            Thread(target=social).start()
