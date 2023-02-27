""" Blueprint for registration endpoints """

from config import client
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from bson.json_util import dumps
import json, ast

# devices endpoints schema
class APIUserSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

# Define the blueprint
blueprint_register = Blueprint(name="blueprint_register", import_name=__name__)

# Select the database and devices collection
db = client.inbox
collection = db.api_users

# Endpoint to register a new device
@blueprint_register.route('/login', methods=["POST"])
@cross_origin()
def add_user():
    """
    Function used to register a new device and API key for private endpoints
    """

    data = request.json
    schema = APIUserSchema()  # Ensure data fits schema

    try:
        # Get the device name from the body
        body = ast.literal_eval(json.dumps(request.get_json()))

        # Validate request body
        schema.load(data)

        # Check whether device already exists
        user = collection.find_one({"username": body['username']})

        if not user or user["password"] != body["password"]:
            return jsonify({"message": "Bad password or user"}), 401

        access_token = create_access_token(identity=body["username"])

        return jsonify(access_token=access_token)

    except ValidationError as err:
        return dumps({"api_key": None, "message": f"An error occurred: {err}"}), 400
    except:
        return dumps({"api_key": None, "message": "An error occurred"}), 500
