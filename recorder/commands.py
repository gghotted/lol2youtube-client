import time

import pyautogui
import pydirectinput
import settings
from api.replay import PlaybackAPI, RecordingAPI, RenderAPI
from requests.exceptions import ConnectionError
from waiting import wait


class Command:
    def execute(self):
        raise NotImplementedError


class Wait(Command):
    def execute(self):
        wait(self.check)

    def check(self):
        raise NotImplementedError


class WaitReady(Wait):
    def check(self):
        try:
            return PlaybackAPI().get().json()['time'] > settings.REPLAY_API_READY_MIN_SEC
        except (ConnectionError, KeyError):
            return False


class WaitCompleteRecord(Wait):
    def check(self):
        return RecordingAPI().get().json()['recording'] == False


class WaitPlayTime(Wait):
    def __init__(self, sec):
        self.sec = sec
    
    def check(self):
        return PlaybackAPI().get().json()['time'] > self.sec


class Sleep(Command):
    def __init__(self, sec):
        self.sec = sec

    def execute(self):
        time.sleep(self.sec)


class SetTime(Command):
    def __init__(self, time):
        self.data = {
            'time': time
        }

    def execute(self):
        PlaybackAPI().post(self.data)


class Record(Command):
    def __init__(self, path, start=-1, end=-1):
        pass

    def execute(self):
        pydirectinput.press('f12')


class PressKey(Command):
    '''
    mac > 시스템 환경설정 > 보안 및 개인 정보 보호 > 개인 정보 보호 > 손쉬운 사용 > vscode, 터미널 추가
    '''
    def __init__(self, keys, **kwargs):
        self.keys = keys
        self.kwargs = kwargs

    def execute(self):
        pydirectinput.press(self.keys, **self.kwargs)
        print(f'{self.keys} pressed!')


class SetRenderProperty(Command):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    
    def execute(self):
        return RenderAPI().post(self.kwargs)
