import requests
from bs4 import BeautifulSoup
import re
from typing import Union, List
from util import async_mesure_time_excute, RateLimiter
import asyncio
import aiohttp
import ast
import random
from lxml import etree

class AmazonScraper(object):

    def __init__(self, scrape_speed: int) -> None:
        self._header = [{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40'},
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78'},
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'},
        {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'},
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}]
        session = requests.Session()
        self._cookies = session.get('https://www.amazon.com/b?node=16225007011',headers=random.choice(self._header)).cookies
        self.scrape_speed = scrape_speed
    
    def get_child_category(self, parent_id: str) -> dict:

        URL = 'https://www.amazon.com/b?node='
        category_information = {}

        r  = requests.get(f'{URL}{parent_id}', headers=random.choice(self._header), cookies=self._cookies)
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
        r  = requests.get(f'https://www.amazon.com/gp/bestsellers/hi/{category_id}', headers=random.choice(self._header), cookies=self._cookies)
        soup = BeautifulSoup(r.text, 'html.parser')
        item = soup.find('div',class_='p13n-desktop-grid').attrs['data-client-recs-list']
        top_item = ast.literal_eval(item)
        url = "https://www.amazon.com" + soup.find('li', class_ = 'a-last').find('a').attrs['href']
        r  = requests.get(url, headers=random.choice(self._header), cookies=self._cookies)
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

        async def get_single_asin(session, url: str):
            async with await session.get(url, headers=random.choice(self._header), cookies=self._cookies) as response:
                # cols_name = ['title','new_price','list_price','rating','rating_count','img_url]
                result = []
                r_text =  await response.text()
                soup = BeautifulSoup(r_text, 'html.parser')
                result.append(soup.find(id='productTitle').text.strip())
                try:
                    avail = soup.find(id='deliveryBlockMessage').text
                    if 'cannot be shipped' in avail:
                        print(f'{url} not in vn')
                        try:
                            #new price on right above corner 
                            new_price = soup.find(id="price_inside_buybox").text.strip()
                            result.append(new_price)
                        except:
                            #new price list on item detail
                            new_price = soup.find('span', class_='a-offscreen').text.strip()
                            result.append(new_price)
                        
                        try:
                            list_price = soup.find('span', class_='a-price a-text-price a-size-base').find('span',class_='a-offscreen').text
                            result.append(list_price)
                        except:
                            #if don't sale list price equal new price
                            result.append(new_price)

                    else:
                        print(f'{url} normal')
                        new_price = soup.find('span', class_='a-price aok-align-center').find('span',class_='a-offscreen').text
                        result.append(new_price)

                        try:
                            list_price = soup.find('span', class_='a-price a-text-price',  attrs={'data-a-size':'s'}).find('span',class_='a-offscreen').text
                            result.append(list_price)
                        except:
                            result.append(new_price)

                except:
                    print(f'{url} unavailabe')
                    result.append('N/A')
                    result.append('N/A')
                result.append(soup.select_one("#acrCustomerReviewText").text)
                result.append(soup.find(id="acrPopover").find('span',class_="a-icon-alt").text)
                dom = etree.HTML(str(soup))
                img_txt = dom.xpath('//*[@id="imageBlock_feature_div"]/script[1]/text()')[0]
                result.append(re.findall(r'https://m.media-amazon.com/images/I/[\w+-.]+.jpg', img_txt)[0])
            return result
        if isinstance(asins, list):
            async with aiohttp.ClientSession() as session:
                session = RateLimiter(session, self.scrape_speed)
                tasks = []
                cols_name = ['title','new_price','list_price','rating','rating_count','img_url']
                for asin in asins:
                    url = 'https://www.amazon.com/dp/' + asin
                    tasks.append(get_single_asin(session,url))
                result = await asyncio.gather(*tasks)
                result.insert(0, cols_name)
            return result

        elif isinstance(asins, str):
            async with aiohttp.ClientSession() as session:
                url = 'https://www.amazon.com/dp/' + asins
                return await get_single_asin(session, url)

    def test(self, asins):
        for id in asins:
            r  = requests.get(f'https://www.amazon.com/dp/{id}', headers=random.choice(self._header), cookies=self._cookies)
            soup = BeautifulSoup(r.text, 'html.parser')
            print(soup.title.text)
            time.sleep(1)

if __name__ == '__main__':
    import pandas as pd
    import time
    scraper = AmazonScraper(2)
    # df = pd.DataFrame(scraper.get_child_category('16225007011'))
    # scraper.get_detail_asin()
    # print(df)
    loop = asyncio.get_event_loop()
    # asins = ['B08QBMD6P4','B06W55K9N6','B09QV692XY','B0795DP124','B07CRG7BBH']
    # asins = 'B08QBMD6P4'
    # # print(title)
    # # print(pd.DataFrame(scraper.best_100_seller_in_category('172504')))
    best_seller = scraper.best_100_seller_in_category('172456')
    # # print(scraper.get_child_category('16225007011'))
    ids = best_seller['asin_id']
    print(scraper._cookies)
    print(scraper._header)
    # print(ids)
    # # time.sleep(2)
    info = loop.run_until_complete(scraper.get_detail_asin(ids[:4]))
    # print(info)
    # df = pd.DataFrame(info[1:],columns=info[0])
    # print(df)
    # print(df)
    # df = pd.DataFrame(info[0])
    # df.to_csv('ca_best_seller.csv')
    # print(df)
    # # print(title)
    # start = time.time()
    # scraper.test(ids)
    # print(round(time.time() - start,4))
    # # print(ids)



    