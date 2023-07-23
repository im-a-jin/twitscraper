import pickle
import time
from collections import deque
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from .utils import FIFOCache, DEFAULT_COOKIE_PATH, get_links_js

class Tweeter:
    def __init__(self, user, cookie_path=DEFAULT_COOKIE_PATH, cache_size=4):
        self.user = user
        with open(cookie_path, "rb") as f:
            self.cookies = pickle.load(f)
        self._get_links_js = get_links_js(user)
        self.cache = FIFOCache(cache_size)
        self.cache_size = cache_size
        self._cache_tweets()

    def _cache_tweets(self):
        """Initializes cache with existing tweets"""
        driver = self._init_driver()
        tweets = {}
        while len(tweets) < self.cache_size:
            links = driver.execute_script(self._get_links_js)
            tweets.update(links)
            time.sleep(1)
        self.cache.update(reversed(tweets.items()))
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
        while not any(t in self.cache for t in tweets):
            links = driver.execute_script(self._get_links_js)
            tweets.update(links)
            time.sleep(1)
        for t in self.cache:
            tweets.pop(t, None)
        self.cache.update(reversed(tweets.items()))
        driver.quit()
        return tweets
