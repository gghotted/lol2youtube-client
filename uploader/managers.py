from datetime import datetime, timedelta
from time import sleep

import requests
import settings

from uploader import (PentakillCollector1Uploader, PentakillCollector2Uploader,
                      PentakillCollector3Uploader)
from uploader.exceptions import UploadException


class UploadManager:
    host = ''
    uploaders = []
    continue_sleep_time = 10
    uploader_error_retry_time = timedelta(hours=1)

    def __init__(self):
        self.uploaders = list(map(
            lambda c: c(),
            self.uploaders
        ))

    def run(self):
        while True:
            self.replay = self.get_replay_info()
            if not self.replay:
                sleep(self.continue_sleep_time)
                continue
                
            uploader = self.get_uploader()
            if not uploader:
                sleep(self.continue_sleep_time)
                continue
            
            try:
                self.video_url = uploader.upload(
                    self.replay['filepath'],
                    self.replay['title'],
                    self.replay['description'],
                )
                self.post_upload_info(uploader.channel_name)
            except UploadException:
                continue

    def get_uploader(self):
        uploaders = sorted(
            filter(lambda u: datetime.now() > self.uploader_error_retry_time + u.last_error_time, self.uploaders),
            key=lambda u: u.last_error_time
        )

        if len(uploaders) == 0:
            return None
        
        return uploaders[0]

    def get_replay_info(self):
        raise NotImplementedError

    def post_upload_info(self, channel_name):
        raise NotImplementedError


class PentakillUploadManager(UploadManager):
    host = settings.DATA_SERVER_HOST
    uploaders = [
        PentakillCollector1Uploader,
        PentakillCollector2Uploader,
        PentakillCollector3Uploader,
    ]

    def get_replay_info(self):
        url = self.host + '/replay/kill/wait-upload'
        res = requests.get(url)
        data = res.json()
        if data.get('id') == None:
            return None
        else:
            return data

    def post_upload_info(self, channel_name):
        url = self.host + '/youtube/upload_info'
        requests.post(url, data={
            'file': self.replay['file'],
            'title': self.replay['title'],
            'description': self.replay['description'],
            'url': self.video_url,
            'channel_name': channel_name,
        })
