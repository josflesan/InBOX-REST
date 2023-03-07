""" Blueprint for users endpoint """

from config import Config
from src.decorators.access_control import AccessControl
from bson import json_util
from bson.objectid import ObjectId
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_socketio import emit
from jwt import encode
from marshmallow import Schema, fields, ValidationError
import json, ast, bcrypt, datetime

# Define Schema for user update
class UserUpdate(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.String(required=False)
    updates = fields.Dict(required=True)

class User(Schema):
    username = fields.String(required=True)
    email = fields.String(required=False)
    password = fields.String(required=True)
    updates = fields.Dict(required=False)

# Helper method to authenticate user
def authenticate(username: str, password: str, db_user: dict) -> bool:
    """
    Method that authenticates a user upon login

    Parameters:
        - username (str): the inputted username
        - password (str): the inputted password
        - db_user (dict): the database user with matched username

    Returns:
        - result (bool): ```True``` if the user was authenticated correctly, otherwise ```False```

    """
    return username == db_user['username'] and bcrypt.checkpw(password.encode('utf-8'), db_user['password'])

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

# Endpoint to login
@blueprint_users.route('/login', methods=['POST'])
@cross_origin()
def login():
    """Method that logs an existing user into the application."""

    try:
        body = ast.literal_eval(json.dumps(request.get_json()))
        User().load(request.json)  # Validate user with schema

        user = collection.find_one({"username": body["username"]})
        if not user:
            return jsonify({"result": False, "err": "The user could not be found!"}), 401
        
        # Authenticate and return token
        elif not authenticate(body["username"], body["password"], user):
            return jsonify({"result": False, "err": "The credentials are invalid"}), 401
        
        token = encode({"user_id": user["hashID"], "role": user["role"], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, Config.SECRET_KEY)
        collection.update_one({"username": body["username"]}, {"$set": {"active": True}})  # Set active flag
        return jsonify({"token": token}), 201
    
    except ValidationError as err:
        return jsonify({"result": False, "err": f"{err}"}), 401

    except Exception as err:
        return jsonify({"result": False, "err": f"An error occurred: {err}"}), 500

# Endpoint to logout
@blueprint_users.route('/logout/<username>', methods=["GET"])
@cross_origin()
@AccessControl.token_required
def logout(username: str):
    """Logout current user."""

    try:
        # Get user and set active to false
        collection.find_one_and_update({"username": username}, {"$set": {"active": False}})
        return jsonify({"result": True}), 201

    except Exception as err:
        return jsonify({"err": f"An error occurred: {err}"}), 500


# Endpoint to get and update users
@blueprint_users.route('/query', methods=["POST", "PUT"])
@cross_origin()
@AccessControl.is_self_or_admin  # Regualr users should only be able to alter their own profiles
def user_query():
    """
    Method that retrieves or updates a single user in the database (used for profile screen)

    Parameters:
        user_id (str): the user id as it appears in the database
    """

    try:
        body = ast.literal_eval(json.dumps(request.get_json()))
        user = collection.find_one({"username": body["username"]})
        if request.method == "POST":
            # Get a user from the database (only user can retrieve their details)
            return json.loads(json_util.dumps(user)), 201

        else:
            # Update a user in the database
            body = ast.literal_eval(json.dumps(request.get_json()))

            updates = {}
            UserUpdate().load(request.json)
            for key in body["updates"].keys():
                if key in ["active", "role", "_id"]:
                    return jsonify({"result": False, "err": "Access denied"}), 401
                elif key in user:
                    updates[key] = body["updates"][key]

            final_update = {"$set": updates}
            collection.update_one({"_id": ObjectId(user['_id'])}, final_update)
    
            return jsonify({"result": True}), 201

    except ValidationError as err:
        return jsonify({"result": False, "err": f"An error occurred: {err}"}), 401    
    
    except Exception as err:
        return jsonify({"result": False, "err": f"An error occurred: {err}"}), 500

# Endpoint to create users
@blueprint_users.route('/register', methods=["POST"])
@cross_origin()
def create_user():
    """
    Method that creates a new user in the database from the request body data
    """

    try:
        # Get the post body from the request
        body = ast.literal_eval(json.dumps(request.get_json()))
        User().load(request.json)  # Validate user with schema

        # Check if user exists, if so return error
        user = collection.find_one({"username": body["username"]})

        if user:
            return jsonify({"result": False, "err": "The username is already taken!"}), 401
        
        # Otherwise, create a user with new details
        salt = bcrypt.gensalt()
        hashedPass = bcrypt.hashpw(body['password'].encode('utf-8'), salt)
        
        collection.insert_one({
            "username": body["username"],
            "password": hashedPass,
            "email": body["email"],
            "active": True,
            "hashID": abs(hash(body["username"])),
            "role": "user"
        })

        return jsonify({"result": True}), 201

    except ValidationError as err:
        return jsonify({"result": False, "err": f"{err}"}), 401
    except Exception as err:
        return jsonify({"result": False, "err": f"An error occurred: {err}"}), 500

# Endpoint to make a user an administrator
@blueprint_users.route('/elevate/<username>', methods=["GET"])
@cross_origin()
@AccessControl.is_admin
def elevate_privileges(username: str):
    """
    Method that elevates a user's privileges. Can only be called by someone
    with a valid API Key

    Parameters:
        - username (str): the user account's username
    """

    try:
        user = collection.find_one_and_update({"username": username}, {"$set": {"role": "admin"}})

        if not user:
            return jsonify({"result": False, "err": "The user could not be found!"}), 401
        
        return jsonify({"result": True}), 201
    
    except Exception as err:
        return jsonify({"result": False, "err": f"An error occurred: {err}"}), 500


# Endpoint to delete user
@blueprint_users.route('/delete', methods=["POST"])
@cross_origin()
@AccessControl.is_self_or_admin
def delete_user():
    """
    Method that deletes a user from the database

    Parameters:
        - username (str): the user account's username
    """
    try:
        body = ast.literal_eval(json.dumps(request.get_json()))
        # Try finding the user in the database and delete if found
        username = body["username"]
        user = collection.find_one_and_delete({"username": username})

        if not user:
            return jsonify({"err": f"The user with username {username} was not found"}), 401
        
        return jsonify({"result": True}), 201

    except Exception as err:
        return jsonify({"err": f"An error occurred: {err}"})
