import signal
import time
from os import kill
from pathlib import Path

import psutil
import pydirectinput
import pygetwindow as gw
import settings
from api.client import ReplayDownLoadAPI, ReplayPathAPI, ReplayWatchAPI
from api.data_server import KillReplay, NotRecordedKillEvent, ReplayBlackList
from api.exceptions import ClientAPIFail
from easydict import EasyDict
from editor.editors import (Editor, MinimapInterfaceEditor,
                            SummonerMinmapInterfaceEditor)
from recorder import (AutoCamKillRecorder, ChallengerFixedCamKillRecorder,
                      FixedCamKillRecorder, VictimAutoCamKillRecorder)


class RecordNotSuccess(Exception): pass


class Manager:
    recorder_class = AutoCamKillRecorder
    editor_class = SummonerMinmapInterfaceEditor
    kill_event_queries = dict()
    host = settings.DATA_SERVER_HOST

    def __init__(self, record_count):
        self.kill_replay_api = KillReplay(host=self.host)
        self.not_recorded_kill_event_api = NotRecordedKillEvent(host=self.host)
        self.replay_blacklist_api = ReplayBlackList(host=self.host)

        self.record_count = record_count
        self.recorded_count = 0
        self.download_dir = self.get_download_dir()

    def run(self):
        while self.is_continuable():
            self.loop()

    def loop(self):
        try:
            self.empty_save_dir()
            kill_events = self.get_kill_events()
            self.download(kill_events[0].timeline)
            self.open_replay(kill_events[0].timeline)
            self.focus_replay_window()
            save_path = self.record(kill_events)
            self.kill_replay_process(kill_events[0].timeline)
            save_path = self.edit_replay(save_path)
            if not settings.TEST_MODE:
                self.send_replay_to_server(kill_events[0].id, save_path)
            self.recorded_count += 1
        except (ClientAPIFail, RecordNotSuccess) as e:
            print(e)
            self.clientapi_except_handle(e, kill_events[0].timeline)

    def empty_save_dir(self):
        for f in settings.REPLAY_SAVE_DIR.iterdir():
            try:
                f.unlink()
            except Exception as e:
                for proc in psutil.process_iter():
                    try:
                        for file in proc.open_files():
                            if Path(file.path).name == f.name:
                                kill(proc.pid, signal.SIGINT)
                                time.sleep(5)
                    except:
                        continue
                f.unlink()

    def edit_replay(self, path):
        return self.editor_class(path, 'replays/result.mp4').excute()

    def focus_replay_window(self):
        time.sleep(15)
        pydirectinput.click(1920 // 2, 1080 // 2)

    def match_id_no_region(self, match_id):
        return match_id.split('_')[1]

    def get_kill_events(self):
        kill_events = self.not_recorded_kill_event_api.get(**self.kill_event_queries).json()
        return [EasyDict(e) for e in kill_events]

    def download(self, match_id, try_count=0):
        if settings.CLIENT_API_MAX_RETRY_COUNT == try_count:
            raise ClientAPIFail('리플레이 다운로드 실패')

        ReplayDownLoadAPI(match_id=self.match_id_no_region(match_id)).post()
        filepath = Path(f'{self.download_dir}/{self.cvt_replay_filename(match_id)}')

        if not filepath.is_file():
            time.sleep(settings.CLIENT_API_RETRY_INTERVAL)
            self.download(match_id, try_count + 1)

    def open_replay(self, match_id, try_count=0):
        if settings.CLIENT_API_MAX_RETRY_COUNT == try_count:
            raise ClientAPIFail('리플레이 오픈 실패')

        ReplayWatchAPI(match_id=self.match_id_no_region(match_id)).post()
        if self.get_process_replay_process_pid(match_id) == None:
            time.sleep(settings.CLIENT_API_RETRY_INTERVAL)
            self.open_replay(match_id, try_count + 1)

    def record(self, kill_events):
        self.recorder_class(kill_events, save_path='').execute()
        save_path = self.get_saved_replay_path()
        self.org_file_path = save_path
        return save_path

    def get_saved_replay_path(self):
        files = list(settings.REPLAY_SAVE_DIR.iterdir())
        if len(files) == 0:
            raise RecordNotSuccess('정상적으로 녹화되지 않습니다.')
        if len(files) > 1:
            raise Exception(f'{settings.REPLAY_SAVE_DIR}에 파일 한 개가 필요합니다.')
        return str(files[0])

    def send_replay_to_server(self, event_id, path):
        with open(path, 'rb') as f, open(self.org_file_path, 'rb') as org_f:
            self.kill_replay_api.post(
                data={
                    'event': event_id
                },
                files={
                    'file': f,
                    'org_file': org_f,
                }
            )

    def kill_replay_process(self, match_id):
        pid = self.get_process_replay_process_pid(match_id)
        kill(pid, signal.SIGINT)
        time.sleep(3)

    def get_process_replay_process_pid(self, match_id):
        replay_name = self.cvt_replay_filename(match_id)
        try:
            lol = next(
                filter(
                    lambda p: p.name() == 'League of Legends.exe', 
                    psutil.process_iter()
                )
            )
            args = lol.cmdline()
            if args[1] != self.download_dir + '/' + replay_name:
                return None
            return lol.pid
        except:
            return None

    def clientapi_except_handle(self, e, match_id):
        self.replay_blacklist_api.post(
            data={
                'match': match_id,
                'msg': str(e),
            }
        )

    def cvt_replay_filename(self, match_id):
        return match_id.replace('_', '-') + '.rofl'

    def is_continuable(self):
        return self.recorded_count < self.record_count

    def get_download_dir(self):
        return ReplayPathAPI().get().json()


class NoneEditorManager(Manager):
    recorder_class = FixedCamKillRecorder

    def send_replay_to_server(self, event_id, path):
        with open(path, 'rb') as f:
            self.kill_replay_api.post(
                data={
                    'event': event_id
                },
                files={
                    'org_file': f
                }
            )
    
    def edit_replay(self, path):
        return path


class UltimateNoneEditorManager(NoneEditorManager):
    recorder_class = VictimAutoCamKillRecorder
    kill_event_queries = {
        'o': '-sequence_ultimate_hit_count',
    }


class SimpleEditorManager(NoneEditorManager):
    recorder_class = FixedCamKillRecorder
    editor_class = Editor


class UltimateSimpleEditorManager(SimpleEditorManager):
    recorder_class = VictimAutoCamKillRecorder
    kill_event_queries = {
        'o': '-sequence_ultimate_hit_count',
    }


class ChallengerSimpleEditorManager(Manager):
    host = settings.CHALLENGER_DATA_SERVER_HOST
    recorder_class = ChallengerFixedCamKillRecorder
    editor_class = Editor


class ChallengerUltimateSimpleEditorManager(ChallengerSimpleEditorManager):
    kill_event_queries = {
        'o': '-sequence_ultimate_hit_count',
    }
