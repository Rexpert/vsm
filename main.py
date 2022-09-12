import pandas as pd
import json
import numpy as np
from itertools import cycle

with open(r'.\data\veg.json', 'r') as f:
    veg_json = json.load(f)

with open(r'.\data\shop.json', 'r') as f:
    shop_json = json.load(f)


shops = pd.DataFrame(veg_json['products'])
shop = pd.DataFrame(shop_json['product'])

(
    shops
    .loc[:, ['pid', 'locationX', 'locationY', 'budget', 'recommended', 'name']]
    # .assign(
    #     # hours = lambda x: x.linkDescription.str.extract(r'^Business Hour : ([^\n]+)(?:\n?\s*)(?:Rest day|Open daily)').iloc[:, 0].str.strip()
    # )
    # .loc[:, ['linkDescription', 'hours']]
    # .to_csv(r'.\output\check.csv', index=False)
)

result = pd.DataFrame(dict(pid=shops.pid, session=np.fromiter(cycle(range(130)), dtype=int, count=shops.shape[0])))
result.to_csv(r'.\output\scrape.csv', index=False)
# def open_or_not(desc):
#     now = pd.Timestamp.now()
#     hour = now.hour
#     dow = now.day_of_week
#     print(desc.lower().split('open daily')[0])

# open_or_not('Business Hour : 11.00am to 2.20pm , 5.20pm to 9.20pm \nOpen daily \nUpdated 14/8/2022\n')