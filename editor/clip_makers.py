from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.all import crop
from moviepy.video.VideoClip import ColorClip


def mute(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).volumex(0)
    return wrapper


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class MainClipMaker:
    w = 1080
    h = 1080

    @staticmethod
    def make(clip, w=w, h=h):
        return crop(
            clip,
            x_center=clip.w / 2,
            width=w,
            y_center=clip.h / 2,
            height=h,
        )


class MinimapMaker:
    @staticmethod
    @mute
    def make(clip, x1=1720, y1=880, x2=1910, y2=1070):
        return crop(
            clip, 
            x1=x1, 
            y1=y1, 
            x2=x2, 
            y2=y2,
        )


class SummonerMaker:
    '''
    interface size = 0

    p1 = Point(3, 102)
    p2 = Point(49, 147)
    p3 = Point(1869, 373)
    '''

    '''
    interface size = 50
    '''

    p1 = Point(3, 128)
    p2 = Point(61, 185)
    p3 = Point(1856, 469)

    '''
    interface size = 100
    p1 = Point(2, 154)
    p2 = Point(74, 224)
    p3 = Point(1843, 566)
    '''
    summoner_w = p2.x - p1.x
    summoner_h = p2.y - p1.y
    summoner_h_interval = ((p3.y - p1.y) / 4) - summoner_h

    @staticmethod
    @mute
    def make(clip, x1, y1):
        return crop(
            clip,
            x1=x1,
            y1=y1,
            width=SummonerMaker.summoner_w,
            height=SummonerMaker.summoner_h,
        )


class SummonerTeamMaker:
    TEAM_LEFT = 0
    TEAM_RIFHT = 1
    x_axis = {
        TEAM_LEFT: SummonerMaker.p1.x,
        TEAM_RIFHT: SummonerMaker.p3.x,
    }

    @staticmethod
    @mute
    def make(clip, team_id, interval_ratio=0.3, order_reverse=False):
        interval = round(SummonerMaker.summoner_w * interval_ratio)
        w = (SummonerMaker.summoner_w * 5) + (interval * 4)
        h = SummonerMaker.summoner_h
        bg = ColorClip(
            (w, h),
            (0, 0, 0),
            duration=clip.duration,
        )
        x = SummonerTeamMaker.x_axis[team_id]
        y_org = SummonerMaker.p1.y
        y_step = h + SummonerMaker.summoner_h_interval
        summoners = []

        for i in range(5):
            y = y_org + (y_step * i)
            summoners.append(SummonerMaker.make(clip, x, y))
        
        y = 0
        x_org = 0
        x_step = SummonerMaker.summoner_w + interval
        if order_reverse:
            summoners.reverse()
        for i, s in enumerate(summoners):
            x = x_org + (x_step * i)
            summoners[i] = s.set_position((x, y))

        return CompositeVideoClip([bg] + summoners)

