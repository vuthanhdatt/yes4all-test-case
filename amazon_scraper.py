import requests
from bs4 import BeautifulSoup
import re
from typing import Union, List
from util import async_mesure_time_excute, RateLimiter
import asyncio
import aiohttp
import ast

class AmazoneScraper(object):

    def __init__(self, scrape_speed: int) -> None:
        self._header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40'}
        session = requests.Session()
        self._cookies = session.get('https://www.amazon.com/b?node=16225007011',headers=self._header).cookies
        self.scrape_speed = scrape_speed
    
    def get_child_category(self, parent_id: str) -> dict:

        URL = 'https://www.amazon.com/b?node='
        category_information = {}

        r  = requests.get(f'{URL}{parent_id}', headers=self._header, cookies=self._cookies)
        soup = BeautifulSoup(r.text, 'html.parser')

        child_cat = soup.find_all('a', class_='a-color-base a-link-normal')
        cat_name = [child.find("span").text for child in child_cat]
        cat_url = ["https://www.amazon.com/"+ child.attrs["href"] for child in child_cat]
        
        cat_id = [re.findall(r"Cn%3A(\d+)", url)[0] for url in cat_url]
        
        category_information['child_cat_name'] = cat_name
        category_information['cat_url'] = cat_url
        category_information['parent_id'] = [parent_id] * len(cat_name)
        category_information['child_id'] = cat_id
        
        return category_information

    def best_100_seller_in_category(self, category_id : str):
        rank = []
        asin_id = []
        result = {}
        r  = requests.get(f'https://www.amazon.com/gp/bestsellers/hi/{category_id}', headers=self._header, cookies=self._cookies)
        soup = BeautifulSoup(r.text, 'html.parser')
        item = soup.find('div',class_='p13n-desktop-grid').attrs['data-client-recs-list']
        top_item = ast.literal_eval(item)
        url = "https://www.amazon.com" + soup.find('li', class_ = 'a-last').find('a').attrs['href']
        r  = requests.get(url, headers=self._header, cookies=self._cookies)
        soup = BeautifulSoup(r.text, 'html.parser')
        item = soup.find('div',class_='p13n-desktop-grid').attrs['data-client-recs-list']
        top_item.extend(ast.literal_eval(item))
        for item in top_item:
            rank.append(item['metadataMap']['render.zg.rank']) 
            asin_id.append(item['id'])
        result['rank'] = rank
        result['asin_id']  = asin_id
        return result
            

    @async_mesure_time_excute
    async def get_detail_asin(self, asins: Union[str, List[str]]):
        title = []
        new_price = []
        list_price = []
        rating_count = []
        rating = []
        img_url = []

        async def get_single_asin(session, url: str):
            async with await session.get(url, headers=self._header, cookies=self._cookies) as response:
                r_text =  await response.text()
                soup = BeautifulSoup(r_text, 'html.parser')
                print(soup.title.text)
                return soup.title.text

        if isinstance(asins, list):
            async with aiohttp.ClientSession() as session:
                session = RateLimiter(session, self.scrape_speed)
                tasks = []

                for asin in asins:
                    url = 'https://www.amazon.com/dp/' + asin
                    tasks.append(get_single_asin(session,url))
                result = await asyncio.gather(*tasks)
            return result

        elif isinstance(asins, str):
            async with aiohttp.ClientSession() as session:
                url = 'https://www.amazon.com/dp/' + asins
                return await get_single_asin(session, url)



if __name__ == '__main__':
    import pandas as pd
    scraper = AmazoneScraper(2)
    # df = pd.DataFrame(scraper.get_child_category('172282'))
    # scraper.get_detail_asin()
    # print(df)
    loop = asyncio.get_event_loop()
    # asins = ['B08QBMD6P4','B06W55K9N6','B09QV692XY','B0795DP124','B07CRG7BBH']
    asins = 'B08QBMD6P4'
    # print(title)
    # print(pd.DataFrame(scraper.best_100_seller_in_category('172504')))
    best_seller = scraper.best_100_seller_in_category(193870011)
    ids = best_seller['asin_id']
    print(len(ids))
    loop.run_until_complete(scraper.get_detail_asin(ids))
    # print(title)



    