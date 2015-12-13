__author__ = 'tomislav'
from app import db
import datetime
from copy import deepcopy
import json

from sqlalchemy.sql import func

class Settings(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Send_to = db.Column(db.String(200))
    Email_password  = db.Column(db.String(200))
    Amazon_user = db.Column(db.String(200))
    Secret_Access_key = db.Column(db.String(200))
    Send_from = db.Column(db.String(200))
    Access_key_ID = db.Column(db.String(200))
    Email_username = db.Column(db.String(200))

    def __init__(self,**kwargs):
        for k,v in kwargs.iteritems():
            setattr(self,k,v)
        db.session.add(self)
        db.session.commit()

class Item(db.Model):

    sdb = db
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    url = db.Column(db.String(200))
    updated = db.Column(db.DateTime())
    old_price = db.Column(db.Float(),default=0.00)
    new_price = db.Column(db.Float(),default=0.00)
    percent = db.Column(db.Integer,default=0.00)
    email_notify = db.Column(db.Integer,default=0)

    def __init__(self,name="",url="",new_price=0):
        self.name = name
        self.url = url
        self.updated = datetime.datetime.now()
        self.old_price = 0.00
        self.new_price = new_price
        self.percent = 100
        self.sdb.session.add(self)
        self.sdb.session.commit()

    def empty(self):
        self.name=""
        self.updated = datetime.datetime.now()
        self.old_price = 0
        self.new_price = 0
        self.percent = 100
        self.sdb.session.commit()

    def from_url(self,url):
        self.url = url
        self.empty()

    def from_asin(self,asin):
        self.url = "http://www.amazon.com/dp/{}".format(asin)
        self.empty()

    def update_price(self,new_price):
        self.old_price = deepcopy(self.new_price)
        self.new_price = new_price
        if self.old_price:
            self.percent = -int((1 - self.new_price/self.old_price)*100)
        self.updated = datetime.datetime.now()
        self.email_notify = 0
        self.sdb.session.commit()

    def __call__(self, *args, **kwargs):
        return {
                'id':self.id,
                'name':self.name,
                'url':self.url,
                'updated':str(self.updated),
                'old_price':self.old_price,
                'new_price':self.new_price,
                'percent':self.percent
            }
    @staticmethod
    def update_all():
        db.session.commit()

    def __repr__(self):
        return json.dumps({
                'id':self.id,
                'name':self.name,
                'url':self.url,
                'updated':str(self.updated),
                'old_price':self.old_price,
                'new_price':self.new_price,
                'percent':self.percent
            })
