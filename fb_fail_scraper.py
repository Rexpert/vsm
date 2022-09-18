import os
import re
import time
from pathlib import Path

import pandas as pd
from facebook_scraper import parse_cookie_file
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait

SECRET_PATH = str(Path.home() / 'secrets' / 'facebook.com_cookies.txt')


def init_driver():
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36')
    caps = DesiredCapabilities().CHROME
    caps['pageLoadStrategy'] = 'eager'
    driver_path = '/usr/local/bin/chromedriver'
    # driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    driver = Chrome(driver_path, options=options, desired_capabilities=caps)
    return driver


def add_cookie(driver):
    cookie = parse_cookie_file(SECRET_PATH)
    driver.get('https://m.facebook.com/')
    for c in cookie:
        driver.add_cookie({'name': c.name, 'value': c.value,
                          'path': c.path, 'expires': c.expires})


def read_data():
    scraped = (
        pd
        .read_csv(r'./output/fb_scrape.csv')
        .assign(
            time=lambda x: pd.to_datetime(x.time),
            scrape=lambda x: pd.to_datetime(x.scrape)
        )
    )
    with open(r'./output/fb_fail.txt', 'r') as f:
        fail = f.read().splitlines()
    fail = [re.sub(r'^(\d+)_(\d+)$', r'https://www.facebook.com/groups/\g<1>/permalink/\g<2>', f) for f in fail]
    return fail, scraped


def scrape(driver, url):
    try:
        driver.get(url)
        now = pd.Timestamp.now()
        time.sleep(2)
        article = driver.find_element_by_css_selector('*[role="article"]')
        like = article.find_element_by_class_name('nnzkd6d7').text
        for a in article.find_elements_by_css_selector('a[role="link"]'):
            try:
                post_time = pd.to_datetime(a.get_attribute('aria-label'))
                break
            except:
                continue
        return pd.DataFrame(dict(original_request_url=url, time=post_time, reaction_count=like, scrape=now), index=[0])
    except Exception as e:
        save_screenshot(driver, r'./screenshot.png')
        raise e
        return pd.DataFrame(columns=['original_request_url'])


def save_screenshot(driver: Chrome, path: str = '/tmp/screenshot.png') -> None:
    # Ref: https://stackoverflow.com/a/52572919/\
    raise Exception
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
    # driver.save_screenshot(path)  # has scrollbar
    Path(path).unlink()
    driver.find_element_by_tag_name('body').screenshot(path)  # avoids scrollbar
    driver.set_window_size(original_size['width'], original_size['height'])


def scrape_all(driver, urls):
    driver.get(urls[0])
    time.sleep(2)
    password = driver.find_elements_by_css_selector('input[name="pass"]')
    if len(password) > 0:
        password[0].send_keys(os.environ['PASSWORD'])
        password[0].send_keys(Keys.ENTER)
        time.sleep(5)
    results = []
    for url in urls:
        results.append(scrape(driver, url))
    return results


if __name__ == '__main__':
    fail, fb_scraped = read_data()
    driver = init_driver()
    add_cookie(driver)
    results = scrape_all(driver, fail)
    driver.quit()
    results.extend([fb_scraped])
    results = pd.concat(results, ignore_index=True)
    results.to_csv(r'./output/fb_scrape.csv', index=False)
    fail = list(set(fail) - set(results.original_request_url))
    if len(fail) > 0:
        with open(r'./output/fb_fail.txt', 'w') as f:
            f.write('\n'.join(fail))
            f.write('\n')
    else:
        Path(r'./output/fb_fail.txt').unlink(missing_ok=True)
