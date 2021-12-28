from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Commenter:
    profile_root_dir = ''
    channel_name = ''
    
    def __init__(self):
        fp = webdriver.FirefoxProfile(self.profile_root_dir)
        self.driver = webdriver.Firefox(fp)

    def comment(self, url, content, fix=True):
        print(url)
        self.driver.get(url)
        sleep(3)

        self.driver.execute_script("window.scrollTo(0, 500)")
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'placeholder-area'))).click()
        self.driver.find_element_by_id('contenteditable-root').send_keys(content)
        self.driver.find_element_by_id('submit-button').click()

        if fix:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#action-menu #button'))).click()
            self.driver.find_element_by_css_selector('tp-yt-paper-item.style-scope.ytd-menu-navigation-item-renderer').click()
            self.driver.find_element_by_id('confirm-button').click()
            sleep(1)


class PentakillCollector1Commenter(Commenter):
    profile_root_dir = 'C:/Users/gghot/AppData/Roaming/Mozilla/Firefox/Profiles/oc9xcyt0.yt-upload1'
    channel_name = '펜타킬 수집가'


class PentakillCollector2Commenter(Commenter):
    profile_root_dir = 'C:/Users/gghot/AppData/Roaming/Mozilla/Firefox/Profiles/8wj1r904.yt-upload2'
    channel_name = '펜타킬 수집가2'


class PentakillCollector3Commenter(Commenter):
    profile_root_dir = 'C:/Users/gghot/AppData/Roaming/Mozilla/Firefox/Profiles/lly51bfj.yt-upload3'
    channel_name = '펜타킬 수집가3'
