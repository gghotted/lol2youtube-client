import settings

from api.base import API


class DataServerAPI(API):
    host = settings.DATA_SERVER_HOST
    verify = True
    data_to_json = False


class NotRecordedKillEvent(DataServerAPI):
    allow_methods = ('get', )
    endpoint = '/event/not-recorded/'


class KillReplay(DataServerAPI):
    allow_methods = ('post', )
    endpoint = '/replay/kill/'


class KillReplayUpdate(DataServerAPI):
    allow_methods = ('patch', )
    endpoint = '/replay/kill/{id}'


class ReplayBlackList(DataServerAPI):
    allow_methods = ('post', )
    endpoint = f'/replay/blacklist/'
