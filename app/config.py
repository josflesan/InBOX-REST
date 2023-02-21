"""Module to configure app to connect with database."""

from pymongo import MongoClient

DATABASE = MongoClient()['inbox']
DEBUG = True
client = MongoClient('localhost', 27017)