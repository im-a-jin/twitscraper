import pickle
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger('generate_cookies')
logger.info("NOTE: This script requires a GUI since it opens Firefox in non-headless mode.")

driver = webdriver.Firefox()
driver.get("https://twitter.com")

wait = WebDriverWait(driver, 60, 1).until(lambda x: x.find_element(By.CSS_SELECTOR, '[data-testid="tweet"]').is_displayed())

cookies = driver.get_cookies()
with open("cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)

driver.quit()
