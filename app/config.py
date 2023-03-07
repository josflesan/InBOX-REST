"""Module to configure app to connect with database."""

from datetime import timedelta
from pymongo import MongoClient

class Config(object):
    DEBUG = True
    SECRET_KEY = "secret!"  #TODO: Change this
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ACCESS_LIFESPAN = {"hours": 24}
    JWT_REFRESH_LIFESPAN = {"days": 30}
    JWT_SECRET_KEY = "super secret"  #TODO: Change this
    CORS_HEADERS = 'Content-Type'
    DATABASE = MongoClient()['inbox']
    DATABASE_CLIENT = MongoClient('localhost', 27017)
    BCRYPT_LOG_ROUNDS = 13
    CS_URL = "https://josflesan.github.io"  # The URL to the Courier-Service

