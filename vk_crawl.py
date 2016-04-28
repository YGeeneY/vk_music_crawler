import pickle
from re import search as re_search
from selenium.webdriver import PhantomJS
from unidecode import unidecode
import logging

from settings import *
logger = logging.getLogger('vk_sniffer')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler('crawler.log')
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s |\t %(asctime)s \t\t [%(levelname)s] \t\t %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class PhantomVkCrawler(PhantomJS):
    def __init__(self):
        super(PhantomVkCrawler, self).__init__()
        logger.info('driver has been created.')
        self.login()

    def get(self, url):
        logger.info('fetching url %s' % url)
        super(PhantomVkCrawler, self).get(url)
        logger.info('url fetched')

    def login(self):
        self.get(VK_ROOT)
        try:
            logger.info('trying to load cookies')
            cookies = pickle.load(open("vk_cookies.pkl", "rb"))
            for cookie in cookies:
                self.add_cookie(cookie)
            logger.info('cookies loaded successfully')
            return

        except FileNotFoundError:
            logger.info('fail to load cookie')
            logger.info('filling authorization form')
            pass

        login_field = self.find_element_by_id('quick_email')
        pwd_field = self.find_element_by_id('quick_pass')
        login_btn = self.find_element_by_id('quick_login_button')
        login_field.send_keys(LOGIN)
        pwd_field.send_keys(PWD)
        login_btn.click()
        logger.info('authorization done!')
        pickle.dump(self.get_cookies(), open("vk_cookies.pkl","wb"))

    def query_vk_audio(self, search):
        result_array = []
        search = unidecode(search)
        self.get(SEARCH_MUSIC_ROOT % search)
        results = self.find_elements_by_class_name('audio')
        for song_node in results:
            td = song_node.find_elements_by_class_name('play_btn_wrap')[0].find_element_by_xpath('..')
            input_ = td.find_elements_by_css_selector('*')[-1]
            link = input_.get_attribute('value')

            id_ = re_search('[\d_]+$', song_node.get_attribute('id')).group()
            title_section = song_node.find_element_by_xpath("//span[contains(@id, '{id}')]".format(id=id_))
            title = title_section.text
            if not title:
                break
            result_array.append(dict(title=title, author=search, url=link))
        logger.info('fetched %s objects' % len(result_array))
        logger.info('return fetch query')
        return result_array
