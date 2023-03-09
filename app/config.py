"""Module to configure app to connect with database."""

from datetime import timedelta
from pymongo import MongoClient

class Config(object):
    DEBUG = True
    API_HOST = "http://localhost:5000/api/v1"
    SECRET_KEY = "secret!"  #TODO: Change this
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ACCESS_LIFESPAN = {"hours": 24}
    JWT_REFRESH_LIFESPAN = {"days": 30}
    CORS_HEADERS = 'Content-Type'
    DATABASE = MongoClient()['inbox']
    DATABASE_CLIENT = MongoClient('localhost', 27017)
    BCRYPT_LOG_ROUNDS = 13
    CS_URL = "https://inbox-hot:8020/courierapp/"

