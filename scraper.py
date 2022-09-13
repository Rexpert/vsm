# 1950 records = 10 days * 13 hours * 15 records
# 1920 records = 24 hours * 4 (15 mins) * 20 records

import json
import multiprocessing as mp
import random
from operator import itemgetter
import sys

import pandas as pd
import requests

HEADERS = {
    'Host': '54.169.161.161',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'User-Agent': 'GoVeggie%20Malaysia/1009 CFNetwork/1209 Darwin/20.2.0',
    'Accept-Language': 'en-gb',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Length': '0',
}
URL = r'http://54.169.161.161/get_product_details2.php'


def scrape(pid):
    s = requests.Session()
    s.headers = HEADERS
    params = {
        'pid': pid,
        'shopType': '0'
    }
    res = s.post(URL, params=params)
    try:
        d = res.json()['product']
    except KeyError as e:
        # pid 5082 not found in database but appear when overall searching
        return pd.DataFrame(columns=['pid'])
    new_data = pd.DataFrame(d)
    return new_data


def scrape_all(to_sc):
    with mp.Pool(processes=mp.cpu_count()) as pool:
        # try:
        result = pool.map(scrape, to_sc)
        # except KeyError:
        #     sys.exit('Unknown Requests Respond')
    return result


def read_data():
    with open(r'./data/veg.json', 'r') as f:
        veg_json = json.load(f)
    try:
        output = pd.read_csv(r'./output/scrape.csv')
    except FileNotFoundError:
        output = pd.DataFrame(columns=['pid'])
    pid = set(map(itemgetter('pid'), veg_json['products']))
    return pid, output


if __name__ == '__main__':
    pid, df = read_data()
    scraped = set(df.pid.astype(int))
    if len(scraped) < len(pid):
        to_sc = random.sample(list(pid - scraped), 20)
        result = scrape_all(to_sc)
        result.extend([df])
        result = pd.concat(result)
        result.to_csv(r'./output/scrape.csv', index=False)
    else:
        sys.exit('Finished Scraping...')
