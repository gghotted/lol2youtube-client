import settings
from manager import Manager

'''
관리자 권한으로 실행해야함
vsoce, cmd를 관리자 권한으로 실행하고 스크립트를 실행

롤 replay의 인터페이스 설정은 롤 클라이언트 재실행시 초기화되는 설정이 있음
체크 리스트
 - 챔피언위 이름 표시
 - 인터페이스 크기
 - 미니맵 크기
 - 채팅창 크기, 위치
'''

if __name__ == '__main__':
    manager = Manager(settings.REPLAY_RECORD_COUNT)
    manager.run()
