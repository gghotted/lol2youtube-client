import random
from time import sleep

import requests
import settings

import commenter
from commenter import (PentakillCollector1Commenter,
                       PentakillCollector2Commenter,
                       PentakillCollector3Commenter)


class CommentManager:
    host = settings.DATA_SERVER_HOST
    commenters = [
        PentakillCollector1Commenter,
        PentakillCollector2Commenter,
        PentakillCollector3Commenter,
    ]
    continue_sleep_time = 10
    items = {
        '갤럭시 버즈2, 12% 할인': 'https://coupa.ng/cbbHXF',
        '아이폰13 PRO, 최대 12% 할인': 'https://coupa.ng/cbfTTC',
        '아이패드 프로, 11% 할인': 'https://coupa.ng/cbfTXe',
    }

    def __init__(self):
        self.commenters = list(map(
            lambda c: c(),
            self.commenters
        ))
    
    def run(self):
        while True:
            self.upload_info = self.get_upload_info()
            if not self.upload_info:
                sleep(self.continue_sleep_time)
                continue
            
            commenter = self.get_commenter(self.upload_info['channel_name'])
            content = self.get_ad_content()
            commenter.comment(
                self.upload_info['url'],
                content,
            )
            self.post_comment_info(content)

    def get_commenter(self, channel_name):
        commenters = filter(
            lambda c: c.channel_name == channel_name,
            self.commenters
        )
        return next(commenters)

    def get_upload_info(self):
        url = self.host + '/youtube/upload_info/not_has_ad'
        res = requests.get(url)
        data = res.json()
        if not data.get('id'):
            return None
        return data
    
    def post_comment_info(self, content):
        requests.post('http://192.168.45.29:8080/youtube/commentad', data={
            'upload_info': self.upload_info['id'],
            'content': content,
        })

    def get_ad_content(self):
        form = '''
{name}: {link}

이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.
        '''
        idx = random.randint(0, len(self.items) - 1)
        item = list(self.items.items())[idx]
        name = item[0]
        link = item[1]
        return form.format(
            name=name,
            link=link,
        ).strip()
