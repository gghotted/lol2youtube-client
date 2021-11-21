import signal
import subprocess
import time
from os import kill
from pathlib import Path

import settings
from api.client import ReplayDownLoadAPI, ReplayPathAPI, ReplayWatchAPI
from api.data_server import KillReplay, NotRecordedKillEvent, ReplayBlackList
from api.exceptions import ClientAPIFail
from easydict import EasyDict
from recorder import FixedCamKillRecorder


class Manager:
    def __init__(self, record_count):
        self.record_count = record_count
        self.recorded_count = 0
        self.download_dir = self.get_download_dir()

    def run(self):
        while self.is_continuable():
            self.loop()

    def loop(self):
        try:
            kill_events = self.get_kill_events()
            self.download(kill_events[0].timeline)
            self.open_replay(kill_events[0].timeline)
            save_path = self.record(kill_events)
            self.send_replay_to_server(kill_events[0].id, save_path)
            self.kill_replay_process(kill_events[0].timeline)
            self.recorded_count += 1
        except ClientAPIFail as e:
            print(e)
            self.clientapi_except_handle(e, kill_events[0].timeline)

    def match_id_no_region(self, match_id):
        return match_id.split('_')[1]

    def get_kill_events(self):
        kill_events = NotRecordedKillEvent().get().json()
        return [EasyDict(e) for e in kill_events]

    def download(self, match_id, try_count=0):
        if settings.CLIENT_API_MAX_RETRY_COUNT == try_count:
            raise ClientAPIFail('리플레이 다운로드 실패')

        ReplayDownLoadAPI(match_id=self.match_id_no_region(match_id)).post()
        filepath = Path(f'{self.download_dir}/{self.cvt_replay_filename(match_id)}.rofl')

        if not filepath.is_file():
            time.sleep(settings.CLIENT_API_RETRY_INTERVAL)
            self.download(match_id, try_count + 1)

    def open_replay(self, match_id, try_count=0):
        if settings.CLIENT_API_MAX_RETRY_COUNT == try_count:
            raise ClientAPIFail('리플레이 오픈 실패')

        ReplayWatchAPI(match_id=self.match_id_no_region(match_id)).post()
        if self.get_process_replay_process_info(match_id) == None:
            time.sleep(settings.CLIENT_API_RETRY_INTERVAL)
            self.open_replay(match_id, try_count + 1)

    def record(self, kill_events):
        save_path = str(settings.REPLAY_SAVE_DIR / (kill_events[0].timeline + '.webm'))
        FixedCamKillRecorder(kill_events, save_path=save_path).execute()
        return save_path

    def send_replay_to_server(self, event_id, path):
        with open(path, 'rb') as f:
            KillReplay().post(
                data={
                    'event': event_id
                },
                files={
                    'file': f
                }
            )

    def kill_replay_process(self, match_id):
        proc_info = self.get_process_replay_process_info(match_id)
        pid = int(proc_info[0])
        kill(pid, signal.SIGINT)
        time.sleep(3)

    def get_process_replay_process_info(self, match_id):
        replay_name = self.cvt_replay_filename(match_id)
        proc = subprocess.Popen(
            f'ps -A | grep {replay_name}.rofl',
            stdout=subprocess.PIPE,
            shell=True
        )
        for line in proc.stdout.readlines():
            line = line.decode()
            info = line.split()
            if 'tty' in info[1]:
                continue
            else:
                return info
        return None

    def clientapi_except_handle(self, e, match_id):
        ReplayBlackList().post(
            data={
                'match': match_id,
                'msg': str(e),
            }
        )

    def cvt_replay_filename(self, match_id):
        return match_id.replace('_', '-')

    def is_continuable(self):
        return self.recorded_count < self.record_count

    def get_download_dir(self):
        return ReplayPathAPI().get().json()
