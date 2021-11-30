import base64

import psutil

from api.base import API

psutil.process_iter

class ClientAPI(API):
    def __init__(self, **kwargs):
        self.port, self.auth = self._get_client_info()
        super().__init__(**kwargs)

    def _get_client_info(self):
        try:
            client = next(
                filter(
                    lambda p: p.name() == 'LeagueClientUx.exe',
                    psutil.process_iter()
                )
            )
            args = client.cmdline()
            port = next(
                filter(
                    lambda arg: arg.startswith('--app-port='),
                    args
                )
            ).split('=')[1]
            auth = next(
                filter(
                    lambda arg: arg.startswith('--remoting-auth-token='),
                    args
                )
            ).split('=')[1]
            return port, auth
        except:
            raise Exception('실행중인 롤 클라이언트를 찾을 수 없습니다.')

    @property
    def host(self):
        return f'https://127.0.0.1:{self.port}'

    @property
    def headers(self):
        token = f'riot:{self.auth}'.encode()
        token = base64.b64encode(token).decode()
        return {'Authorization': f'Basic {token}'}


class ReplayDownLoadAPI(ClientAPI):
    allow_methods = ('post', )
    endpoint = '/lol-replays/v1/rofls/{match_id}/download'


class ReplayWatchAPI(ClientAPI):
    allow_methods = ('post', )
    endpoint = '/lol-replays/v1/rofls/{match_id}/watch'


class ReplayPathAPI(ClientAPI):
    allow_methods = ('get', )
    endpoint = '/lol-replays/v1/rofls/path'
