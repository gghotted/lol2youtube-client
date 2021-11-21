import settings
from manager import Manager

if __name__ == '__main__':
    manager = Manager(settings.REPLAY_RECORD_COUNT)
    manager.run()
