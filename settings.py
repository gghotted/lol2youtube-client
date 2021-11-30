import json
from pathlib import Path


def set(key, default):
    '''
    json 파일로부터 값 할당, 존재하지 않을 시 default값 할당.
    '''
    with open('secrets.json', 'r') as f:
        globals()[key] = json.load(f).get(key, default)


set('DATA_SERVER_HOST', 'http://localhost:8000')

# 리플레이 조작 가능한 최소 시점
set('REPLAY_API_READY_MIN_SEC', 10)

set('REPLAY_SAVE_DIR', Path(__file__).parent / 'replays')

set('REPLAY_RECORD_COUNT', 100)

set('CLIENT_API_RETRY_INTERVAL', 2)

set('CLIENT_API_MAX_RETRY_COUNT', 5)

set('TEST_MODE', False)

g = globals()
if g['TEST_MODE']:
    g['REPLAY_RECORD_COUNT'] = 1
    