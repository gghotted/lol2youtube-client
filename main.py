import manager
import settings

'''
관리자 권한으로 실행해야함
vsoce, cmd를 관리자 권한으로 실행하고 스크립트를 실행

롤 replay의 인터페이스 설정은 롤 클라이언트 재실행시 초기화되는 설정이 있음
체크 리스트
 - 챔피언위 이름 표시(챔피언 이름)
 - 인터페이스 크기(50%)
 - 미니맵 크기(0%)
 - 채팅창 크기, 위치(안보이게 위치)
 - 사운드(ingame 75%, pc 100%)
 - 반디캠 확인
 - 창모드 x
'''

if __name__ == '__main__':
    for manager_name in settings.MANAGER_NAME:
        manager_class = getattr(manager, manager_name)
        m = manager_class(settings.REPLAY_RECORD_COUNT)
        m.run()
