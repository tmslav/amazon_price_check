__author__ = 'tomislav'
from celery.decorators import periodic_task,task
from .amazon_api import  ProductAdvertisingAPI
from .models import Settings
from datetime import timedelta,datetime
import logging
import requests
import lxml.html
import re


from .models import Item

class Parser:
    def __call__(self, *args, **kwargs):
        return lxml.html.fromstring(args[0].text)

    @staticmethod
    def get_price_value(price_string):
        price_string = price_string.replace(",", ".")
        price = re.search('[^\d]*([\d]+(\.\d\d)?).*', price_string)
        if price:
            result = float(price.group(1))
        else:
            result = None
        return result

class AmazonCrawler:
    session = requests.session()

    def extract_price(self,sel,item):
        price = sel.xpath("//span[@id='priceblock_dealprice']")
        if not price:
            price = sel.xpath("//span[@id='priceblock_ourprice']")
        if price:
            price = Parser.get_price_value(price[0].text)
        if not price:
            logging.error("no price found for url={}".format(item.url))
            import ipdb;ipdb.set_trace()
        else:
            return price

    def extract_name(self,sel,item):
        name = sel.xpath("//span[@id='productTitle']")
        if name:
            return name[0].text
        else:
            logging.error("no name found for url={}".format(item.url))
            return None

    def parse(self,item):
        parser = Parser()
        sel = parser(self.session.get(item.url))
        price = self.extract_price(sel,item)
        name = self.extract_name(sel,item)
        item.name = name;
        item.update_price(price)

class AmazonAPICrawler(ProductAdvertisingAPI):
    def get_asin_from_url(self,url):
        asin = re.findall("\/dp\/([A-Z0-9]+)",url)
        if asin:
            return asin[0]
        else:
            return None

    def parse(self,id,crawler):
        i = Item.query.filter_by(id=id).one()

        asin_from_url = self.get_asin_from_url(i.url)
        asin = asin_from_url if "http" not in asin_from_url else i.url

        if asin:
            pd = self.item_lookup([asin])
            if pd:
                i.name = pd[asin]['title']
                i.update_price(pd[asin]['price'])
            else:
                i.name = "wrong url or asin"
                i.update_price(-1)

def call_amazon_api_task(i):
    crawler = AmazonAPICrawler()
    crawler.parse(i.id,crawler)

@periodic_task(run_every=timedelta(seconds=5))
def check_database_for_new_items():
    i = Item.query.filter_by(new_price=0).first()
    if i:
        call_amazon_api_task(i)
    else:
        i = Item.query.filter_by(old_price=0).first()
        if i:
            call_amazon_api_task(i)

@periodic_task(run_every=timedelta(seconds=5))
def update_listing():
    since = datetime.now() - timedelta(minutes=5)
    i = Item.query.filter(Item.updated<since).first()
    call_amazon_api_task(i)


@periodic_task(run_every=timedelta(seconds=5))
def send_email():
    import smtplib

    pd = Settings.query.all()[-1]
    items = Item.query.filter(Item.percent>-5 ).filter_by(email_notify=0)
    fromaddr = pd.Email_username
    toaddrs  = pd.Send_to

    msg ="Hello,\n"
    for i in items:
        msg += 'Item {} has changed his price from {} to {}. \n'.format(i.url,i.old_price,i.new_price)
        i.email_notify = 1
        i.update_all()

    if items.count()>0:
        username = pd.Email_username
        password = pd.Email_password
        import ipdb;ipdb.set_trace()
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.ehlo()
        server.starttls()
        server.login(username,password)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
