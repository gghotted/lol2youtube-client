from moviepy.editor import CompositeVideoClip, VideoFileClip
from moviepy.video.fx.all import crop
from moviepy.video.VideoClip import ColorClip

from editor.clip_makers import (MainClipMaker, MinimapMaker, SummonerMaker,
                                SummonerTeamMaker)


class Editor:
    def __init__(self, filepath, result_path=None):
        self.clip = VideoFileClip(filepath)
        self.result_path = filepath
        if result_path:
            self.result_path = result_path

    def excute(self):
        self.get_final_clip().write_videofile(self.result_path)
        return self.result_path

    def get_final_clip(self):
        '''
        상속하여 clip을 composite할때는 audio를 0으로 해야함을 주의
        '''
        return MainClipMaker().make(self.clip)


class MinimapInterfaceEditor(Editor):
    minimap_position = ('left', 'bottom')

    def get_final_clip(self):
        main = MainClipMaker.make(self.clip)
        minimap = MinimapMaker.make(self.clip)
        return CompositeVideoClip([
            main,
            minimap.set_position(self.minimap_position),
        ])


class SummonerMinmapInterfaceEditor(Editor):
    summoner_height = 80
    minimap_height = 200
    bg_height = MainClipMaker.h + summoner_height + minimap_height
    minimap_position = ('center', 'bottom')

    def get_final_clip(self):
        main = MainClipMaker.make(self.clip)
        minimap = MinimapMaker.make(self.clip).resize(height=self.minimap_height)
        bg = ColorClip(
            (MainClipMaker.w, self.bg_height),
            color=(0, 0, 0),
            duration=self.clip.duration
        )
        team1 = SummonerTeamMaker.make(
            self.clip,
            SummonerTeamMaker.TEAM_LEFT,
            interval_ratio=0.2,
            order_reverse=True,
        ).resize(height=self.summoner_height)
        team2 = SummonerTeamMaker.make(
            self.clip,
            SummonerTeamMaker.TEAM_RIFHT,
            interval_ratio=0.2,
        ).resize(height=self.summoner_height)

        return CompositeVideoClip([
            bg,
            main.set_position(('center', self.summoner_height)),
            minimap.set_position(self.minimap_position),
            team1.set_position(('left', 'top')),
            team2.set_position(('right', 'top')),
        ])
