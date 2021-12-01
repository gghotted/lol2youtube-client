from moviepy.editor import CompositeVideoClip, VideoFileClip
from moviepy.video.fx.all import crop


class Editor:
    width: int = None
    height: int = None

    def __init__(self, filepath, result_path=None):
        self.clip = VideoFileClip(filepath)
        self.result_path = filepath
        if result_path:
            self.result_path = result_path
    
    def excute(self):
        self.cropped = self.crop()
        clips = self.get_cropped_objects()
        clips.insert(0, self.cropped)
        result = CompositeVideoClip(clips)
        result.write_videofile(self.result_path, threads=4)
        return self.result_path

    def crop(self):
        if self.width == self.clip.w and self.height == self.clip.h:
            return self.clip
        return crop(
            self.clip,
            x_center=self.clip.w / 2,
            width=self.width,
            y_center=self.clip.h / 2,
            height=self.height,
        )

    def get_cropped_objects(self):
        '''
        영상에 추가할 항목을 리턴하는 함수를 작성하세요
        '''
        objects = []
        for name in dir(self):
            if name.startswith('cropped_object_'):
                f = getattr(self, name)
                objects.append(f(self.clip).volumex(0))
        return objects


class SimpleInterfaceEditor(Editor):
    width = 1080
    height = 1080

    def cropped_object_minimap(self, clip):
        return crop(clip, x1=1720, y1=880, x2=1910, y2=1070).set_position(
            ('left', 'top')
        )
