import json
import requests
from bs4 import BeautifulSoup
import boto3
import os

import sys
import logging
import psycopg2


conn_string = "dbname='zaradb' port='5432' user='ZhiqingWang' password='wza12345' host='zaradb.cbkjdr0egrir.us-east-2.rds.amazonaws.com'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
cursor.execute("select system_env_host('ramasankarmolleti.com')")
conn.commit()
cursor.close()
print("working")
exit(0)
# import re

rds_host  = rds_config.db_host
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=15)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

user_agent = os.environ['USER_AGENT']

headers = {"User-Agent": user_agent}

def zara_parse(url):
    zara_page = requests.get(url, headers=headers)
    if zara_page.status_code == '200':
        logger.info("SUCCESS: Connection to website accepted")
    else:
        logger.error(f"ERROR: Connection to website refused, with status_code = {zara_page.status_code}")
        
    zara_soup = BeautifulSoup(zara_page.content, 'html.parser')
    products = zara_soup.findAll('li',{'class','product-grid-product'})
    prices = zara_soup.findAll('span',{'class','price-current__amount'})
    all_product_info = []
    
    for product, price in zip(products, prices):
        try:
            product_info = {}
            product_info['productLink'] = product.a['href']
            product_info['imgLink'] = product.a.div.div.div.img['src']
            product_info['description'] = product.a.div.div.div.img['alt']
            product_info['price'] = price.text
            if len(product_info) == 4:
                all_product_info.append(product_info)
        except (AttributeError, TypeError) as e:
            logger.error("Data not added due to incomplete information")
    
    logger.info(f"Parsed {str(all_product_info)} data to database")
    logger.info('The following are examples of parsed data')
    for item in all_product_info[:10]:
        logger.info(item)
        
def lambda_handler(event, context):
    requested_url = 'https://www.zara.com/us/en/woman-dresses-l1066.html?v1=1180427'
    zara_parse(requested_url)
    return None