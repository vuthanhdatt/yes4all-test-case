import argparse
import asyncio

import pandas as pd

from amazon_scraper import AmazonScraper

amz = AmazonScraper(2)

def main(prams):

    if prams.get_child_category:
        raw_child_cat = amz.get_child_category(prams.get_child_category)
        df = pd.DataFrame(raw_child_cat)
        print(df)

    if prams.best_seller_items:
        raw_best_seller_item = amz.best_100_seller_in_category(prams.best_seller_items)
        df = pd.DataFrame(raw_best_seller_item)
        print(df)   

    if prams.detail_asin_info:
        loop = asyncio.get_event_loop()
        raw_asin_info= loop.run_until_complete(amz.get_detail_asin(prams.detail_asin_info))
        df = pd.DataFrame(raw_asin_info[1:],columns=raw_asin_info[0])
        print(df)   



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Demo Yes4All Test Case')

    parser.add_argument('-gcc','--get-child-category', help='Get children categories information of given parent category')
    parser.add_argument('-bsi','--best-seller-items', help='Get 100 best seller items of given category')
    parser.add_argument('-dai','--detail-asin-info',nargs='+', help='Get detail information of given asin item')
    args = parser.parse_args()

    main(args)

    