""" Blueprint for users endpoint """

from config import Config
from src.decorators.access_control import AccessControl
from bson import json_util
from bson.objectid import ObjectId
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from jwt import encode
from marshmallow import Schema, fields, ValidationError
from random import randint
from email.mime.text import MIMEText
import json, ast, bcrypt, datetime, smtplib, requests

# Define Schema for user update
class UserUpdate(Schema):
    username = fields.String(required=False)
    password = fields.String(required=True)
    email = fields.String(required=True)
    updates = fields.Dict(required=True)

class User(Schema):
    username = fields.String(required=False)
    email = fields.String(required=True)
    password = fields.String(required=True)
    updates = fields.Dict(required=False)

# Helper method to authenticate user
def authenticate(email: str, password: str, db_user: dict) -> bool:
    """
    Method that authenticates a user upon login

    Parameters:
        - email (str): the inputted email
        - password (str): the inputted password
        - db_user (dict): the database user with matched email

    Returns:
        - result (bool): ```True``` if the user was authenticated correctly, otherwise ```False```

    """
    return email == db_user['email'] and bcrypt.checkpw(password.encode('utf-8'), db_user['password'])

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

        user = collection.find_one({"email": body["email"]})
        if not user:
            return jsonify({"result": False, "err": "The user could not be found!"}), 401
        
        # Authenticate and return token
        elif not authenticate(body["email"], body["password"], user):
            return jsonify({"result": False, "err": "The credentials are invalid"}), 401
        
        token = encode({"user_id": user["hashID"], "role": user["role"], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, Config.SECRET_KEY)
        collection.update_one({"email": body["email"]}, {"$set": {"active": True}})  # Set active flag

        endpoint = Config.API_HOST + f"/users/{body['email']}/verification"
        response = requests.get(endpoint)

        return jsonify({"token": token}), 201
    
    except smtplib.SMTPException as err:
        return jsonify({"result": False, "err": f"An error occurred when sending the email: {err}"})

    except ValidationError as err:
        return jsonify({"result": False, "err": f"{err}"}), 401

    except Exception as err:
        return jsonify({"result": False, "err": f"An error occurred: {err}"}), 500

# Endpoint to logout
@blueprint_users.route('/logout/<email>', methods=["GET"])
@cross_origin()
@AccessControl.token_required
def logout(email: str):
    """Logout current user."""

    try:
        # Get user and set active to false
        collection.find_one_and_update({"email": email}, {"$set": {"active": False}})
        return jsonify({"result": True}), 201

    except Exception as err:
        return jsonify({"err": f"An error occurred: {err}"}), 500

# Endpoint to send verification code for 2FA
@blueprint_users.route('/<email>/verification', methods=["GET"])
@cross_origin()
def send_verification(email: str):
    """
    Method to send verification code to user

    Parameters:
        - email (str): the user account's email
    """

    try:
        # Generate random 4 digit code for 2FA and store
        four_digit_code = ''.join([str(randint(0, 9)) for _ in range(0, 4)])
        collection.update_one({"email": email}, {"$set": {"authentication_code": four_digit_code}})

        # Send email for 2FA
        msg = MIMEText(f"Here is your authentication code: {four_digit_code}")
        msg['Subject'] = "InBoX App Authentication"
        msg['From'] = "inboxsmartparcelbox@gmail.com"
        msg['To'] = "josue.fle.sanc@gmail.com"  #TODO: Change this to recipient email
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login("inboxsmartparcelbox@gmail.com", "tstiwvyxaommgzko")
        smtp_server.sendmail("inboxsmartparcelbox@gmail.com", email, msg.as_string())
        smtp_server.quit()

        return jsonify({"result": True}), 201
    
    except smtplib.SMTPException as err:
        return jsonify({"result": False, "err": f"Email could not be sent: {err}"}), 401

    except Exception as err:
        return jsonify({"err": f"Internal Server Error: {err}"}), 500

# Endpoint to get and update users
@blueprint_users.route('/query', methods=["POST", "PUT"])
@cross_origin()
@AccessControl.is_self_or_admin  # Regular users should only be able to alter their own profiles
def user_query():
    """
    Method that retrieves or updates a single user in the database (used for profile screen)

    Parameters:
        user_id (str): the user id as it appears in the database
    """

    try:
        body = ast.literal_eval(json.dumps(request.get_json()))
        user = collection.find_one({"email": body["email"]})
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
                elif key == "email" and collection.find_one({"email": body["updates"][key]}):
                    new_email = body["updates"][key]
                    return jsonify({"result": False, "err": f"The email {new_email} is already taken"}), 401
                
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
        user = collection.find_one({"email": body["email"]})

        if user:
            return jsonify({"result": False, "err": "The email is already taken!"}), 401
        
        # Otherwise, create a user with new details
        salt = bcrypt.gensalt()
        hashedPass = bcrypt.hashpw(body['password'].encode('utf-8'), salt)
        
        collection.insert_one({
            "password": hashedPass,
            "email": body["email"],
            "active": True,
            "hashID": abs(hash(body["email"])),
            "role": "user"
        })

        return jsonify({"result": True}), 201

    except ValidationError as err:
        return jsonify({"result": False, "err": f"{err}"}), 401
    except Exception as err:
        return jsonify({"result": False, "err": f"An error occurred: {err}"}), 500

# Endpoint to resolve 2FA
@blueprint_users.route('/twofactor/<email>/<code>', methods=["GET"])
@cross_origin()
@AccessControl.token_required
def resolve_twofactor(email: str, code: str):
    """
    Method that resolves a 2FA prompt, can only be called with valid API key

    Parameters:
        - email (str): user account email
        - code (str): 8-digit code sent via email to user
    """

    try:
        user = collection.find_one({"email": email})

        if not user:
            return jsonify({"err": "The user was not found!"}), 401
        
        elif user["2fa"] != code:
            return jsonify({"err": "The code is invalid, please try again!"}), 401
        
        return jsonify({"result": True}), 201
    
    except Exception as err:
        return jsonify({"err": f"Internal Server Error: {err}"}), 500

# Endpoint to make a user an administrator
@blueprint_users.route('/elevate/<email>', methods=["GET"])
@cross_origin()
@AccessControl.is_admin
def elevate_privileges(email: str):
    """
    Method that elevates a user's privileges. Can only be called by admin
    with a valid API Key

    Parameters:
        - email (str): the user account's email
    """

    try:
        user = collection.find_one_and_update({"email": email}, {"$set": {"role": "admin"}})

        if not user:
            return jsonify({"result": False, "err": "The user could not be found!"}), 401
        
        return jsonify({"result": True}), 201
    
    except Exception as err:
        return jsonify({"result": False, "err": f"An error occurred: {err}"}), 500


# Endpoint to delete user
@blueprint_users.route('/delete', methods=["DELETE"])
@cross_origin()
@AccessControl.is_self_or_admin
def delete_user():
    """
    Method that deletes a user from the database
    """
    try:
        body = ast.literal_eval(json.dumps(request.get_json()))
        # Try finding the user in the database and delete if found
        email = body["email"]
        user = collection.find_one_and_delete({"email": email})

        if not user:
            return jsonify({"err": f"The user with email {email} was not found"}), 401
        
        return jsonify({"result": True}), 201

    except Exception as err:
        return jsonify({"err": f"An error occurred: {err}"})
