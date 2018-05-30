from datetime import datetime, timedelta
from random import randint
from time import sleep


class Twitter:

    day_limit = 3
    hour_limit = 1

    def __init__(self, data):

        self._data = data
        self._api = data._api

    def __call__(self, social):

        week_posted = self.get_posts(social, 'my_wall', week=1)
        if len(week_posted) >= social['limit']:
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

        week_posts = self.get_posts(social, 'ico_wall', week=1)
        week_can_post = self.cut_posted(week_posts, week_posted)

        if week_can_post:
            for num in range(hour_posts_allow):
                if num+1 <= day_posts_allow:
                    if num+1 <= week_posts_allow:
                        week_can_post.reverse()
                        try:
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
                posts = self._api.twitter.GetUserTimeline(
                    screen_name=target, max_id=max_id)
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
                    else:  # FOR TARGET
                        return_posts.append(post)
                else:
                    return return_posts
            if posts_given:
                return return_posts
            max_id = posts[-1].id-1


class Poster:

    def __init__(self, data):
        self._data = data
        self.twitter = Twitter(data)

    def __getitem__(self, key):
        return {
            'twitter': self.twitter,
            'facebook': self.facebook,
            'telegram': self.telegram
            }[key]

    def __call__(self):
        for line in self._data:
            for social in line['social']:
                social['week_start'] = line['week_start']
                status = self[social['name']](social)
                del social['week_start']
                if status:
                    sleep(randint(40, 80))

    def facebook(self, social):
        pass

    def telegram(self, social):
        pass
