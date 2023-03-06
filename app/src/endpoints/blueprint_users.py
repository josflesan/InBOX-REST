""" Blueprint for users endpoint """

from config import Config
from flask import Blueprint, jsonify, request
from flask_login import *
from flask_bcrypt import *
from flask_cors import cross_origin
from flask_socketio import emit
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, ValidationError
import json, ast

# users endpoints schema

class NewUser(Schema):
    username = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)

# Define the blueprint
blueprint_users = Blueprint(name="blueprint_users", import_name=__name__)

# Select the database and the collection
db = Config.DATABASE_CLIENT.inbox
collection = db.users

# Test endpoint for Users
@blueprint_users.route('/test', methods=['GET'])
@cross_origin()
def test():
    """
    Test endpoint to ping REST-API
    """
    output = {"msg": "I'm the test endpoint from blueprint_users"}
    return jsonify(output)

# Endpoint to update and get users
@blueprint_users.route('/<user_id>', methods=['GET', 'PUT'])
@cross_origin()
def user_query(user_id):
    """
    Method that retrieves or updates a single user in the database

    Parameters:
        user_id (str): the user id as it appears in the database
    """

    pass

# Endpoint to create users
@blueprint_users.route('/create', methods=["PUT"])
@cross_origin()
def create_user():
    """
    Method that creates a new user in the database from the request body data
    """
    pass


