__author__ = 'tomislav'
from .models import Item,Settings
from app import db
db.create_all()

