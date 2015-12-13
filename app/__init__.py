__author__ = 'tomislav'
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import  Api
from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],include=['app.celery_tasks'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app = Flask(__name__,static_folder='templates/static')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379',
app.config['CELERY_RESULT_BACKEND'] ='redis://localhost:6379'


db = SQLAlchemy(app)
api = Api(app)
celery_app = make_celery(app)


