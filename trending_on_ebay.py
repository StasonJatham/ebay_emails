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

