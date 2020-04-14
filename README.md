# ebay_emails

[![forthebadge](https://forthebadge.com/images/badges/oooo-kill-em.svg)](https://forthebadge.com)

Some refactoring needs to be done.

## How To
This script does: 
1. Scrape eBay for E-Mail Addresses
2. Scrape Twitter and Paetbin for Password Dumps
3. It saves these into a Database 
4. It cross references if any eBay seller account has been compromised

## Notice:
you will need a config file with your twitter api key 

```python
with open('tokens_twitter.pickle', 'rb') as handle:
    tokens = pickle.load(handle)

cons_key = tokens["cons_key"] 
cons_sec = tokens["cons_sec"] 
accs_tok = tokens["accs_tok"] 
accs_sec = tokens["accs_sec"] 
```
## Little something:
This will get you the curreent trends oof ebay items.
```python
import requests
from bs4 import BeautifulSoup
import time 
from fake_useragent import UserAgent

def random_header():
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    return(headers)

class Ebaytrend():

    def __init__(self):
        pass

    def get_items(self):

        list_all_items = []

        all_ebay_trending = ["https://www.ebay.de/trending/",
                            "https://www.ebay.com/trending/",
                            "https://www.ebay.co.uk/trending/"
                            ]

        for trend in all_ebay_trending:
            response = requests.get(trend, headers=random_header())
            soup = BeautifulSoup(response.text, 'html.parser')
            time.sleep(2)

            trending_items = soup.select('div > div > div > h2')

            for item in trending_items:
                list_all_items.append(item.a.contents[0])

        return list_all_items
```

