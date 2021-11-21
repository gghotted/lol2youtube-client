from api.base import API


class ReplayControlAPI(API):
    host = 'https://127.0.0.1:2999'
    allow_methods = ('get', 'post')


class RecordingAPI(ReplayControlAPI):
    endpoint = '/replay/recording'


class PlaybackAPI(ReplayControlAPI):
    endpoint = '/replay/playback'


class RenderAPI(ReplayControlAPI):
    endpoint = '/replay/render'


class SequenceAPI(ReplayControlAPI):
    endpoint = 'replay/sequence'
