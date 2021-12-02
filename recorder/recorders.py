import time

from recorder.commands import (PressKey, Record, SetRenderProperty, SetTime,
                               Sleep, WaitCompleteRecord, WaitPlayTime,
                               WaitReady)


class Recorder:
    def __init__(self, save_path):
        self.save_path = save_path
        self.start_time = self.get_start_time()
        self.end_time = self.get_end_time()

    def get_commands(self):
        raise NotImplementedError

    def get_start_time(self):
        raise NotImplementedError

    def get_end_time(self):
        raise NotImplementedError

    def execute(self):
        commands = self.get_commands()
        for command in commands:
            command.execute()

            if isinstance(command, WaitReady):
                self.on_ready()

    def on_ready(self):
        setter = SetRenderProperty(
            interfaceReplay=False,
            interfaceTimeline=False,
            interfaceChat=False,
            interfaceAnnounce=True,
            interfaceScoreboard=False,
            interfaceScore=False,
            interfaceMinimap=True,
            interfaceFrames=True,
        )
        setter.execute()
        setter.execute()


class FixedCamKillRecorder(Recorder):

    def __init__(self, kill_events, start_offset=-20, end_offset=8, **kwargs):
        self.kill_events = kill_events
        self.start_offset = start_offset
        self.end_offset = end_offset
        super().__init__(**kwargs)

    def get_start_time(self):
        return (self.kill_events[0].time / 1000) + self.start_offset

    def get_end_time(self):
        return (self.kill_events[-1].time / 1000) + self.end_offset

    def get_commands(self):
        return [
            # replay 조작 가능 시점까지 기다림
            WaitReady(),

            # 첫 시점 이동 요청 후 랜더링이 깨지는 버그가 있음
            # -> dummy 시점 이동
            SetTime(0),
            Sleep(3),

            # 리플레이 시점 이동
            # 요청 후 안정화 시간으로 10초 대기
            SetTime(self.start_time - 10),
            Sleep(9),

            # 챔피언 화면 고정
            PressKey(self._get_fixed_cam_key(), presses=2),
            Sleep(1),

            # 현 시점부터 end_time까지 녹화
            Record(self.save_path, -1, self.end_time),
            WaitCompleteRecord(),
        ]

    def _get_fixed_cam_key(self):
        key_maps = '12345qwert'
        index = self.kill_events[0].killer.index - 1
        return key_maps[index]


class AutoCamKillRecorder(FixedCamKillRecorder):
    def get_commands(self):
        return [
            # replay 조작 가능 시점까지 기다림
            WaitReady(),

            # 첫 시점 이동 요청 후 랜더링이 깨지는 버그가 있음
            # -> dummy 시점 이동
            SetTime(0),
            Sleep(3),

            # 리플레이 시점 이동
            # 요청 후 안정화 시간으로 10초 대기
            SetTime(self.start_time - 10),
            Sleep(9),

            # 수동으로 오토 카메라 설정
            PressKey('d', presses=2),
            Sleep(0.5),

            # 현 시점부터 end_time까지 녹화
            PressKey('f12'),
            WaitPlayTime(self.end_time),
            PressKey('f12'),
            Sleep(1),
        ]
