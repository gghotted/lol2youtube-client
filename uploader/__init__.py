import re
from collections import deque
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from uploader.exceptions import UploadException


class DoneButtonEnabled(EC.element_to_be_clickable):
    def __call__(self, driver):
        element = super().__call__(driver)
        if element == False:
            return False
        try:
            if element.get_attribute('aria-disabled') == 'false':
                return element
        except:
            return False


class VideoUrlEnabled(EC.element_to_be_clickable):
    def __call__(self, driver):
        element = super().__call__(driver)
        if element == False:
            return False
        url = element.get_attribute('href')
        url_regex = re.compile('https:\/\/youtu\.be\/.{11}$')
        if len(url_regex.findall(url)) == 1:
            return element
        else:
            return False


class Uploader:
    profile_root_dir = ''
    channel_name = ''
    url = 'https://www.youtube.com/upload'

    def __init__(self):
        fp = webdriver.FirefoxProfile(self.profile_root_dir)
        self.driver = webdriver.Firefox(fp)
        self.last_error_time = datetime.min

    def upload(self, filepath, title, description):
        self.driver.get(self.url)

        self.filepath = filepath
        self.title = title
        self.description = description

        method_names = sorted(
            filter(
                lambda m: m.startswith('_process'),
                dir(self),
            )
        )
        for method_name in method_names:
            method = getattr(self, method_name)
            method()

        return self.video_url

    def _process1_set_file(self):
        self.driver.find_element_by_xpath('//input[@type="file"]').send_keys(
            self.filepath
        )

    def _process2_get_video_url(self):
        try:
            ele = WebDriverWait(self.driver, 20).until(VideoUrlEnabled((By.CSS_SELECTOR, '.style-scope.ytcp-video-info[href]')))
        except Exception as e:
            self.last_error_time = datetime.now()
            print(e)
            raise UploadException()
        self.video_url = ele.get_attribute('href')

    def _process3_set_title(self):
        ele = self.driver.find_element_by_id('textbox')
        ele.click()
        ele.send_keys(Keys.CONTROL + 'a')
        ele.send_keys(self.title)

    def _process4_set_description(self):
        ele = self.driver.find_elements_by_id('textbox')[1]
        ele.click()
        ele.send_keys(Keys.CONTROL + 'a')
        ele.send_keys(self.description)

    def _process5_select_kid(self):
        not_kid = self.driver.find_element_by_name('VIDEO_MADE_FOR_KIDS_NOT_MFK')
        not_kid.click()

    def _process6_next_page(self):
        next = self.driver.find_element_by_xpath('//*[contains(text(), "다음")]')
        next.click()
        next.click()
        next.click()

    def _process7_select_public(self):
        self.driver.find_element_by_name('PUBLIC').click()

    def _process8_click_done(self):
        done = WebDriverWait(self.driver, 10).until(DoneButtonEnabled((By.ID, 'done-button')))
        done.click()

    def _process9_wait_complete(self):
        text = '업로드 완료 ... 곧 처리 시작됨'
        WebDriverWait(self.driver, 600).until(EC.presence_of_element_located(
            (By.XPATH, f'//*[contains(text(), "{text}")]')
        ))
        sleep(5)

    def _check_error(self):
        msg = self.driver.find_element_by_xpath('//*[@id="error-message"]').text
        if not msg:
            return
        
        self.last_error_time = datetime.now()
        raise UploadException


class PentakillCollector1Uploader(Uploader):
    profile_root_dir = 'C:/Users/gghot/AppData/Roaming/Mozilla/Firefox/Profiles/oc9xcyt0.yt-upload1'
    channel_name = '펜타킬 수집가'


class PentakillCollector2Uploader(Uploader):
    profile_root_dir = 'C:/Users/gghot/AppData/Roaming/Mozilla/Firefox/Profiles/8wj1r904.yt-upload2'
    channel_name = '펜타킬 수집가2'


class PentakillCollector3Uploader(Uploader):
    profile_root_dir = 'C:/Users/gghot/AppData/Roaming/Mozilla/Firefox/Profiles/lly51bfj.yt-upload3'
    channel_name = '펜타킬 수집가3'
