import os
import logging
from collections import OrderedDict

AUTH_COOKIE_PATH = os.path.join(os.path.dirname(__file__), "auth_cookie.pkl")

def get_links_js(user):
    return f'''
        tweets = document.querySelectorAll('[data-testid="tweet"]')
        last = tweets[tweets.length-1]
        var user_tweets = []
        for (let i = 0; i < tweets.length; i++) {{
            let t = tweets[i]
            if (t.querySelector('a[href^="/{user}/status/" i]') && t.childNodes[0].childNodes[0].childNodes[0].childNodes[0].childElementCount == 1) {{
                user_tweets.push(t)
            }}
        }}
        var links = {{}}
        for (let i = 0; i < user_tweets.length; i++) {{
            let t = user_tweets[i].querySelector('a[href^="/{user}/status/" i]')
            links[t.getAttribute('href')] = t.childNodes[0].getAttribute('datetime')
        }}
        if (last != null) {{
            last.scrollIntoView()
        }}
        return links
    '''
