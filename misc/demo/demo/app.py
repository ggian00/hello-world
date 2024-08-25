import time
from io import StringIO
import os
from logging import getLogger

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

LOGGER = getLogger('demo')

OUTPUT = 'output'

CONFIG = {
    'MINE': os.environ['MINE'],
    'API': os.environ['API'],
}

def main():
    # get clients from mine
    clients = crawl(CONFIG['MINE'])
    clients.set_index('ID', inplace=True)
    clients.index.name = 'id'
    # print(clients.dtypes)

    # create api class object
    api = ShopApi(CONFIG['API'])

    # get User info
    users = [ api.getUser(id) for id in clients.index.values ]
    users_df = pd.DataFrame([flatten_dict(user) for user in users])
    users_df.set_index('id', inplace=True)
    users_df.drop(columns=['__v'], inplace=True)  # remove useless column

    # get all Carts
    carts = api.getCarts()
    carts_df = pd.DataFrame.from_records(carts)
    ncarts_per_user = carts_df.groupby('userId').size().to_frame('ncarts')

    # update Users with number of carts
    # with this way we don't get NaN values
    users_df['ncarts'] = 0
    users_df.update(ncarts_per_user)

    # get products from carts
    # for each product in each cart, create a new entry with full info (imagine a SQL table after a join)
    products_in_carts = [ {'cartId': cart['id'], 'userId': cart['userId'], 'date': cart['date'], 'productId': product['productId'], 'quantity': product['quantity']}  for cart in carts for product in cart['products']]
    products_in_carts_df = pd.DataFrame(products_in_carts)

    # get product info for each product in the carts
    products_info = [ api.getProduct(id) for id in products_in_carts_df['productId'].unique() ]
    products_info_df = pd.DataFrame([flatten_dict(item) for item in products_info])
    products_info_df.set_index('id', inplace=True)

    # calculate unique buyers and total sold count for each product
    unique_users_per_product = products_in_carts_df.groupby('productId')['userId'].nunique().to_frame('unique_buyers')
    total_count_per_product = products_in_carts_df.groupby('productId')['quantity'].sum().to_frame('sold_count')

    # save the final result
    final_products_info_df = products_info_df.join(unique_users_per_product).join(total_count_per_product)
    final_products_info_df.to_excel(f'{OUTPUT}/products.xlsx')
    users_df.to_excel(f'{OUTPUT}/users.xlsx')

    print('Script ended succefssfully')
    print('Check xslx files for results')



def crawl(url):
    #chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    #driver = webdriver.Chrome(options=chrome_options)
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)

    table = driver.find_element(By.CSS_SELECTOR, "#userTable")
    df1 = pd.read_html(StringIO(table.get_attribute('outerHTML')))[0]

    button = driver.find_element(By.CSS_SELECTOR, "#pagination a:not(.active)[href='#']")
    button.click()

    time.sleep(1)

    table = driver.find_element(By.CSS_SELECTOR, "#userTable")
    df2 = pd.read_html(StringIO(table.get_attribute('outerHTML')))[0]

    return pd.concat([df1, df2], ignore_index=True)


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class ShopApi:
    WAIT_TIME = 3

    def __init__(self, url) -> None:
        self.url = url
        self._last_fetch_time = 0

    def _get(self, url):
        time_delta = time.time() - self._last_fetch_time

        if self._last_fetch_time and time_delta < ShopApi.WAIT_TIME:
            sleep = ShopApi.WAIT_TIME - time_delta
            print(f'{self.__class__.__name__} sleeping for {sleep} seconds')
            time.sleep(sleep)

        response = requests.get(url)
        self._last_fetch_time = time.time()

        if response.status_code != 200:
            raise RuntimeError(f"Failed to retrieve data: {response.status_code}")

        return response.json()

    def getProduct(self, id):
        url = f'{self.url}/products/{id}'
        return self._get(url)

    def getCarts(self):
        url = f'{self.url}/carts'
        return self._get(url)

    def getUser(self, id):
        url = f'{self.url}/users/{id}'
        return self._get(url)

if __name__ == '__main__':
    main()
