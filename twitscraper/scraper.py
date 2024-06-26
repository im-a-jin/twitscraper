from datetime import datetime
import logging
import pickle
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from .utils import get_links_js, AUTH_COOKIE_PATH

class Tweeter:
    logger = logging.getLogger('Tweeter')

    def __init__(self, cookie_path=AUTH_COOKIE_PATH):
        with open(cookie_path, "rb") as f:
            self.cookies = pickle.load(f)
        self.users = {}
        self.driver = None

    def _start(self, user='elonmusk'):
        # NOTE: using Elon Musk's homepage as test page
        """
        Start headless Firefox instance.

        Stops and returns -1 if twitter fails to load.
        """
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Firefox(options=options)
        try:
            self.driver.get("https://twitter.com")
            for c in self.cookies:
                self.driver.add_cookie(c)
            if self._get(user) == -1:
                return -1
        except TimeoutException as e:
            self.logger.error("Failed to log in to twitter. Stopping webdriver.")
            self._stop()
            return -1

    def _get(self, user, wait_timeout=60, poll_frequency=1):
        """
        Gets a twitter user's feed and waits for it to load. 
        
        Returns -1 if feed fails to load within the timeout.
        """
        self.driver.get(f"https://twitter.com/{user}")
        try:
            wait = WebDriverWait(self.driver, wait_timeout, poll_frequency).\
                    until(lambda x: x.find_element(By.CSS_SELECTOR, '[data-testid="tweet"]').is_displayed())
        except TimeoutException as e:
            self.logger.error(f"Failed to access/find tweets at https://twitter.com/{user}")
            return -1

    def _stop(self):
        """
        Stops the webdriver.
        """
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()
        self.driver = None

    def add_user(self, user, check=False):
        """
        Adds a user to the Tweeter userlist.

        check queries the user's account to see if their tweets are visible
        but also induces significant I/O overhead

        Returns the time when the user was added to the tweetlist; None if
        user's tweets cannot be accessed.
        """
        if check:
            if self._start(user) == -1:
                self._stop()
                return -1
        self.users[user] = datetime.utcnow().isoformat(sep='T', timespec='milliseconds')
        return self.users[user]

    def remove_user(self, user):
        """
        Removes a user from the Tweeter userlist.

        Returns None if the user does not exist.
        """
        return self.users.pop(user, None)

    def peek(self, user=None, limit=10):
        """
        Checks the user(s) feed for new tweets.

        limit dictates the maximum number of script executions
        """
        tweets = {}
        if self._start() == -1:
            return tweets
        if user is None:
            for u in list(self.users):
                tweets[u] = self._peek(u, limit)
        else:
            tweets[user] = self._peek(user, limit)
        self._stop()
        for k, v in tweets.items():
            tweets[k] = sorted(list(v.items()), key=lambda x: x[1])
        return tweets

    def _peek(self, user, limit=10):
        """
        Helper method for peek.
        """
        i, tweets = 0, {}
        if self._get(user) == -1:
            return tweets
        script = get_links_js(user)
        while i < limit and sum(ti < self.users[user] for ti in tweets.values()) < 2:
            links = self.driver.execute_script(script)
            tweets.update(links)
            time.sleep(1)
            i += 1
        tweets = {tw: ti for tw, ti in tweets.items() if ti > self.users[user]}
        if len(tweets) > 0:
            self.users[user] = max(self.users[user], max(tweets.values()))
        return tweets
