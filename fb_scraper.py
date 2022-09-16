# 1949 records = 20 hours * 2 (30 mins) * 50 records

import multiprocessing as mp
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from facebook_scraper import get_posts, set_user_agent

SECRET_PATH = str(Path.home() / 'secrets' / 'facebook.com_cookies.txt')
VSM_DATA_PATH = r'./output/scrape.csv'
FB_DATA_PATH = r'./output/fb_scrape.csv'
FAIL_PATH = r'./output/fb_fail.txt'
SAMPLE_COUNT = 50

set_user_agent(
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")


def read_data():
    vsm_data = pd.read_csv(VSM_DATA_PATH)
    try:
        fb_data = pd.read_csv(FB_DATA_PATH)
    except FileNotFoundError:
        fb_data = pd.DataFrame(columns=['original_request_url'])
    try:
        with open(FAIL_PATH, 'r') as f:
            fail = f.read().splitlines()
    except FileNotFoundError:
        fail = []
    return vsm_data, fb_data, fail


def find_unscraped(vsm_urls, fb_urls, fail):
    # return which fb.original_request_url is not in vsm.fbLink
    dif = vsm_urls[~vsm_urls.isin(fb_urls)].to_list()
    dif = set(dif) - set(fail)
    return list(dif)


def scrape(urls):
    now = pd.Timestamp.now()
    col = ['original_request_url', 'time', 'reaction_count']
    try:
        gen = get_posts(post_urls=urls, cookies=SECRET_PATH)
        ls_gen = list(gen)
        result = (
            pd
            .DataFrame(ls_gen)
            .loc[:, col]
            .dropna()
            .assign(scrape=now)
        )
    except:
        raise ValueError(urls)
        result = pd.DataFrame(columns=col)
    return result


def scrape_all(urls, n=mp.cpu_count()):
    # split urls 1D-array into n-length 2D-array
    resized_urls = np.resize(urls, (n, int(len(urls)/n))).tolist()
    if len(urls)%n != 0:
        resized_urls[-1].extend(urls[-(len(urls)%n):])
    with mp.Pool(processes=n) as pool:
        results = pool.map(scrape, resized_urls)
    return results


if __name__ == '__main__':
    vsm_data, fb_data, fail = read_data()
    dif = find_unscraped(vsm_data.fbLink.str.strip(), fb_data.original_request_url, fail)
    if len(dif) > 0:
        if len(dif) > SAMPLE_COUNT:
            to_sc = random.sample(dif, SAMPLE_COUNT)
        else:
            to_sc = dif
        results = scrape_all(to_sc)
        results.extend([fb_data])
        results = pd.concat(results)
        new_fail = list(set(to_sc) - set(results.original_request_url))
        if len(new_fail) > 0:
            with open(FAIL_PATH, 'a+') as f:
                f.write('\n'.join(new_fail))
                f.write('\n')
        fail.extend(new_fail)
        import re
        fb_data = results.copy()
        fail = [re.sub(r'[^\d]+\/(\d+)\/[^\d]+\/(\d+)', r'\g<1>_\g<2>', f) for f in fail]
        try:
            results = scrape_all(fail, n=len(fail))
        except:
            raise ValueError(fail)
        results.extend([fb_data])
        results = pd.concat(results)
        new_fail = list(set(fail) - set(results.original_request_url))
        if len(new_fail) > 0:
            with open(FAIL_PATH, 'w') as f:
                f.write('\n'.join(new_fail))
                f.write('\n')
        results.to_csv(FB_DATA_PATH, index=False)
    else:
        sys.exit('Finished Scraping...')
        
