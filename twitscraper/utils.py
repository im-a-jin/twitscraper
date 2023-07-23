import os
import logging
from collections import OrderedDict

DEFAULT_COOKIE_PATH = os.path.join(os.path.dirname(__file__), "cookies.pkl")

def get_links_js(user):
    return f'''
        tweets = document.querySelectorAll('[data-testid="tweet"]')
        last = tweets[tweets.length-1]
        var user_tweets = []
        for (let i = 0; i < tweets.length; i++) {{
            let t = tweets[i]
            if (t.querySelector('a[href^="/{user}/status/"]') && t.childNodes[0].childNodes[0].childNodes[0].childNodes[0].childElementCount == 1 && t.querySelector('[data-testid="socialContext"]') == null) {{
                user_tweets.push(t)
            }}
        }}
        var links = {{}}
        for (let i = 0; i < user_tweets.length; i++) {{
            let t = user_tweets[i].querySelector('a[href^="/{user}/status/"]')
            links[t.getAttribute('href')] = t.childNodes[0].getAttribute('datetime')
        }}
        if (last != null) {{
            last.scrollIntoView()
        }}
        return links
    '''

class FIFOCache(OrderedDict):
    logger = logging.getLogger('FIFOCache')

    def __init__(self, cache_size=None):
        self.cache_size = cache_size
        self.logger.debug(f"Cache size set to {cache_size}")
        OrderedDict.__init__(self)

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_cache_size()

    def _check_cache_size(self):
        if self.cache_size is not None:
            self.logger.debug(f"Checking cache size. Current size is {len(self)}")
            while len(self) > self.cache_size:
                self.popitem(last=False)
