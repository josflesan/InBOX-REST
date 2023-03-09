"""Module containing some decorator functions pertaining to access control"""

from config import Config
from flask import jsonify, request
from marshmallow import Schema, fields
from jwt import decode
from functools import wraps
import ast, json

class User(Schema):
    username = fields.String(required=False)
    email = fields.String(required=True)
    password = fields.String(required=True)
    updates = fields.Dict(required=False)

class AccessControl:

    db = Config.DATABASE_CLIENT.inbox
    collection = db.users

    @staticmethod
    def token_required(func):
        """
        Generic decorator method that checks whether a user has been logged in
        """
        @wraps(func)
        def decorated(*args, **kwargs):
            headers = request.headers
            bearer = headers.get('Authorization')
            token = bearer.split()[1]

            if not token:
                return jsonify({"err": "Token is missing!"}), 401
            
            try:
                decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            except Exception as err:
                return jsonify({"err": f"Token is invalid!: {err}"}), 401
            
            return func(*args, **kwargs)
        
        return decorated
    
    @staticmethod
    def is_admin(func):
        """
        Decorator method that checks for a valid API Key and admin role from caller
        """
        @wraps(func)
        def decorator(*args, **kwargs):

            token = request.headers.get('Authorization').split()[1]

            if not token:
                return jsonify({"err": "The token is missing! Please log in again"}), 401
            
            try:
                decoded_key = decode(token, Config.SECRET_KEY, algorithms=["HS256"])

                if not decoded_key["role"] == "admin":
                    return jsonify({"err": "You do not have permissions to access this endpoint"}), 401
                
            except Exception as err:
                return jsonify({"err": f"Internal server error: {err}"}), 500


            return func(*args, **kwargs)
        
        return decorator
    
    @staticmethod
    def is_self_or_admin(func):
        """
        Decorator method that ensures that API key is valid and user making the request is self
        """
        @wraps(func)
        def decorator(*args, **kwargs):

            token = request.headers.get('Authorization').split()[1]
            body = ast.literal_eval(json.dumps(request.get_json()))
            user = AccessControl.collection.find_one({"email": body["email"]})

            if not token:
                return jsonify({"err": "The token is missing! Please log in again"}), 401
            
            try:
                decoded_key = decode(token, Config.SECRET_KEY, algorithms=["HS256"])

                if not decoded_key["user_id"] == user["hashID"] and decoded_key["role"] != "admin":
                    return jsonify({"err": "You do not have permissions to access this endpoint"}), 401
                
            except Exception as err:
                return jsonify({"err": f"Internal server error: {err}"}), 500


            return func(*args, **kwargs)
        
        return decorator

