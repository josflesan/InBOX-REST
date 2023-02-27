"""Module to configure app to connect with database."""

from pymongo import MongoClient

# MongoDB Stuff
DATABASE = MongoClient()['inbox']
DEBUG = True
client = MongoClient('localhost', 27017)

# Hosting Stuff
CS_URL = "https://josflesan.github.io"  # The URL to the Courier-Service
