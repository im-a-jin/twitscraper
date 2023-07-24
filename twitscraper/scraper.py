import pickle
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from .utils import FIFOCache, get_links_js

class Tweeter:
    def __init__(self, user, cookie_path):
        self.user = user
        with open(cookie_path, "rb") as f:
            self.cookies = pickle.load(f)
        self._get_links_js = get_links_js(user)
        self.latest = "1970-01-01T00:00:00Z"
        self._init_latest()

    def _init_latest(self):
        """Checks twitter feed and updates latest time"""
        driver = self._init_driver()
        links = driver.execute_script(self._get_links_js)
        self.latest = max(links.values())
        driver.quit()

    def _init_driver(self):
        """Start headless Firefox instance"""
        options = Options()
        options.add_argument('-headless')
        options.add_argument('-disable-blink-features=AutomationControlled')
        driver = webdriver.Firefox(options=options)
        driver.get("https://twitter.com")
        for c in self.cookies:
            driver.add_cookie(c)
        driver.get(f"https://twitter.com/{self.user}")
        wait = WebDriverWait(driver, 30, 1).until(lambda x: x.find_element(By.CSS_SELECTOR, '[data-testid="tweet"]').is_displayed())
        return driver

    def peek(self):
        """Peek at feed for new tweets"""
        driver = self._init_driver()
        tweets = {}
        while all(ti > self.latest for tw, ti in tweets.items()):
            links = driver.execute_script(self._get_links_js)
            tweets.update(links)
            time.sleep(1)
        driver.quit()
        tweets = {tw: ti for tw, ti in tweets.items() if ti > self.latest}
        if len(tweets) > 0:
            self.latest = max(tweets.values())
        return reversed(tweets.items())
