import asyncio
from os import path

import pandas as pd
from sqlalchemy import create_engine

from amazon_scraper import AmazonScraper

scraper = AmazonScraper(2)

USERNAME = 'postgres'
PASSWORD = 'root'
HOST = 'localhost'
PORT = '5432'
DB = 'amazon_scrape'
engine = create_engine(f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}')
engine.connect()


def ingest_category(category_id):
    try:
        raw = scraper.get_child_category(category_id)
        df = pd.DataFrame(raw)
        df = df.reindex(columns=['parent_id','parent_cat_name','child_id','child_cat_name','cat_url'])
        df['child_id'] = df['child_id'].astype('int')
        df['parent_id'] = df['parent_id'].astype('int')
        #Ingest to category table in amazon_scrape db
        TABLE_NAME = 'category'
        df.to_sql(name=TABLE_NAME, con=engine, if_exists='replace', index=False)
        print('Ingest category data to database successfully')
        #Ingest to local data folder
        df.to_csv('data/category.csv', index=False)
        print('Ingest category data to local folder successfully')
    except:
        print('ERROR WHEN INGEST CATEGORY DATA. CHECK AGAIN!!!')

def ingest_best_seller(category_id):
    try:
        raw = scraper.best_100_seller_in_category(category_id)
        df = pd.DataFrame(raw)
        df = df.reindex(columns=['rank','asin_id','cat_id','asin_url'])
        df['cat_id'] = df['cat_id'].astype('int')
        df['rank'] = df['rank'].astype('int8')
        TABLE_NAME = 'best_seller'
        df.to_sql(name=TABLE_NAME, con=engine, if_exists='append', index=False)
        print('Ingest best seller data to database successfully')
        if path.exists(f"data/{TABLE_NAME}.csv"):
            df.to_csv(f'data/{TABLE_NAME}.csv', mode='a', index=False, header=False)
        else:
            df.to_csv(f'data/{TABLE_NAME}.csv', mode='w', index=False)
        print('Ingest best seller data to local folder successfully')
    except:
        print('ERROR WHEN INGEST BEST SELLER DATA. CHECK AGAIN!!!')


def ingest_asin_info(asin_id):
    try:
        loop = asyncio.get_event_loop()
        info = loop.run_until_complete(scraper.get_detail_asin(asin_id))
        df = pd.DataFrame(info[1:],columns=info[0])
        TABLE_NAME = 'asin_info'
        df.to_sql(name=TABLE_NAME, con=engine, if_exists='append', index=False)

        print('Ingest asin information data to database successfully')

        if path.exists(f"data/{TABLE_NAME}.csv"):
            df.to_csv(f'data/{TABLE_NAME}.csv', mode='a', index=False, header=False)
        else:
            df.to_csv(f'data/{TABLE_NAME}.csv', mode='w', index=False)

        print('Ingest asin informationr data to local folder successfully')
    except:
        print('ERROR WHEN INGEST ASIN INFO DATA. CHECK AGAIN!!!')


if __name__ == '__main__':

    pass

    ##############################################################################
    ######## UNCOMMENT BELOW LINE OF CODE TO INGEST CRAWL DATA TO DATABASE #######
    ##############################################################################

    
    # ingest_category('16225007011')

    # ingest_best_seller('172456') #Computer Accessories & Peripherals
    # ingest_best_seller('193870011') #Computer Components
    # ingest_best_seller('1292110011') #Data Storage

    # cap_best_item = scraper.best_100_seller_in_category('172456')['asin_id']
    # ingest_asin_info(cap_best_item)
    # cc_best_item = scraper.best_100_seller_in_category('193870011')['asin_id']
    # ingest_asin_info(cc_best_item)
    # ds_best_item = scraper.best_100_seller_in_category('1292110011')['asin_id']
    # ingest_asin_info(ds_best_item)
    
