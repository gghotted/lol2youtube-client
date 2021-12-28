import shutil
from time import sleep

import requests
import settings
from api.data_server import KillReplayUpdate

from editor.editors import Editor


class EditorManager:
    host = settings.DATA_SERVER_HOST
    editor_class = Editor
    continue_sleep_time = 10
    result_path = 'result.mp4'

    def run(self):
        while True:
            self.replay = self.get_replay_info()
            if not self.replay:
                sleep(self.continue_sleep_time)
                continue
            filename = self.download_file(self.replay['org_file_url'])
            self.editor_class(filename, self.result_path).excute()
            self.post_result()
    
    def get_replay_info(self):
        url = self.host + '/replay/kill/need-edit'
        res = requests.get(url)
        data = res.json()
        if data.get('id') == None:
            return None
        return data

    def post_result(self):
        with open(self.result_path, 'rb') as f:
            KillReplayUpdate(id=self.replay['id']).patch(
                files={
                    'shorts_file': f,
                }
            )
    
    def download_file(self, url):
        tempfile = 'temp.mp4'
        with requests.get(url, stream=True) as r:
            with open(tempfile, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return tempfile
                
        
        