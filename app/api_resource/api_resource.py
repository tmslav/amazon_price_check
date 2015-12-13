from flask_restful import Resource
from flask import request,session,jsonify
import datetime
from app.models import Item,Settings

import json

class AddUrlsResource(Resource):
    def post(self):
        try:
            pd = json.loads(request.get_data())
            for url in pd:
                i = Item()
                i.from_url(url)
        except:
            return "",500

class AddAsinsResource(Resource):
    def post(self):
        try:
            pd = json.loads(request.get_data())
            for asin in pd:
                i = Item()
                i.from_asin(asin)
        except:
            return "",500

class SettingsResource(Resource):
    def post(self):
        try:
            pd = request.get_json()
            dict_in = dict((k.replace(" ","_"),v) for k,v in pd.iteritems())
            Settings(**dict_in)
            return "",200
        except:
            return "",500

    def get(self):
        ret = {}
        try:
            last = Settings.query.order_by(Settings.id.desc()).first()
            for k,_ in last.__dict__.iteritems():
                if k!='_sa_instance_state':
                    ret[k.replace("_"," ")]=getattr(last,k)
            return ret,200
        except:
            return "",400

class ItemResourceList(Resource):
    def get(self):
        ret = []
        items = Item.query.all()
        for i in items:
            ret.append(i())
        return ret

    def post(self):
        try:
            pd = json.loads(request.get_data())
            i=Item(pd['name'],pd['url'],float(pd['price']))
            return jsonify(id=i.id)
        except:
            return "",500

class ItemResource(Resource):
    def get(self,item_id):
        return Item.query.filter_by(id=item_id)[0]()

    def put(self,item_id):
        i = Item.query.filter_by(id=item_id)[0]
        try:
            pd = json.loads(request.get_data())
            for k,v in pd.iteritems():
                if k == 'updated':
                    setattr(i,k,datetime.datetime.now())
                else:
                    setattr(i,k,v)
            i.update_all()
            return 201
        except:
            return "",500

    def delete(self,item_id):
        try:
            Item.query.filter_by(id=item_id).delete()
            Item.update_all()
            return '',204
        except:
            return '',500
