# 1949 records = 20 hours * 2 (30 mins) * 50 records

import multiprocessing as mp
import random
import sys
from pathlib import Path

import pandas as pd
from facebook_scraper import get_posts, set_user_agent

SECRET_PATH = str(Path.home() / 'secrets' / 'facebook.com_cookies.txt')
VSM_DATA_PATH = r'./output/scrape.csv'
FB_DATA_PATH = r'./output/fb_scrape.csv'
SAMPLE_COUNT = 15

set_user_agent(
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")


def read_data():
    vsm_data = pd.read_csv(VSM_DATA_PATH)
    try:
        fb_data = pd.read_csv(FB_DATA_PATH)
    except FileNotFoundError:
        fb_data = pd.DataFrame(columns=['original_request_url'])
    return vsm_data, fb_data


def find_unscraped(vsm_urls, fb_urls):
    # return which fb.original_request_url is not in vsm.fbLink
    return vsm_urls[~vsm_urls.isin(fb_urls)].to_list()


def scrape(urls):
    now = pd.Timestamp.now()
    col = ['original_request_url', 'time', 'reaction_count']
    # try:
    gen = get_posts(post_urls=urls, cookies=SECRET_PATH)
    ls_gen = list(gen)
    result = (
        pd
        .DataFrame(ls_gen)
        .loc[:, col]
        .assign(scrape=now)
    )
    # except:
    #     result = pd.DataFrame(columns=col)
    return result


def scrape_all(urls):
    with mp.Pool(processes=mp.cpu_count()) as pool:
        results = pool.map(scrape, urls)
    return results


if __name__ == '__main__':
    vsm_data, fb_data = read_data()
    dif = find_unscraped(vsm_data.fbLink.str.strip(), fb_data.original_request_url)
    if len(dif) > 0:
        if len(dif) > SAMPLE_COUNT:
            to_sc = random.sample(dif, SAMPLE_COUNT)
        else:
            to_sc = dif
        results = scrape_all(to_sc)
        results.extend([fb_data])
        results = pd.concat(results)
        results.to_csv(FB_DATA_PATH, index=False)
    else:
        sys.exit('Finished Scraping...')
        