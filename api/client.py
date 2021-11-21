import base64
import re
import subprocess

from api.base import API


class ClientAPI(API):
    def __init__(self, **kwargs):
        self.port, self.auth = self._get_client_info()
        super().__init__(**kwargs)

    def _get_client_info(self):
        proc = subprocess.Popen(
            'ps -A | grep LeagueClientUx',
            stdout=subprocess.PIPE,
            shell=True
        )
        lines = proc.stdout.readlines()

        port_pat = re.compile('--app-port=(.*?)\ ')
        auth_pat = re.compile('--remoting-auth-token=(.*?)\ ')
        for line in lines:
            line = line.decode()
            port = port_pat.findall(line)
            auth = auth_pat.findall(line)
            if port and auth:
                return port[0], auth[0]

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
