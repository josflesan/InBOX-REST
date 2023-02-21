"""Blueprint for deliveries endpoint"""

from config import client, CS_URL
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, ValidationError
import json
import ast

# Define Delivery Schema used for validation
class DeliverySchema(Schema):
    hashCode = fields.String(required=True)
    userId = fields.String(required=True)

# Define the blueprint
blueprint_deliveries = Blueprint(name="blueprint_deliveries", import_name=__name__)

# Select the database
db = client.inbox
# Select the collection
collection = db.deliveries

# Test endpoint
@blueprint_deliveries.route('/test', methods=['GET'])
def test():
    """
    Test endpoint to ping REST-API
    """
    output = {"msg": "I'm the test endpoint from blueprint_deliveries"}
    return jsonify(output)

# Get delivery function
@blueprint_deliveries.route('/<delivery_id>', methods=['GET'])
def get_delivery(delivery_id):
    """
    Function to retrieve a single delivery record.
    """

    try:
        # Try to fetch the delivery with this id
        delivery_fetched = collection.find_one({ "_id": ObjectId(delivery_id) })

        if delivery_fetched:
            return dumps(delivery_fetched)
        else:
            # No delivery was found
            return "No delivery was found", 404

    except:
        # Error while trying to fetch the delivery
        return "The delivery could not be fetched", 500

# Toggle scanned value
@blueprint_deliveries.route('/<delivery_id>', methods=['PUT'])
def toggle_scanned(delivery_id):
    """
    Function that updates the scanned flag of a delivery record (true/false)
    """

    try:
        delivery = collection.find_one({"_id": ObjectId(delivery_id)})
        update = collection.update_one({"_id": ObjectId(delivery_id)}, {"$set": { "scanned": not delivery['scanned'] }})

        if update:
            return f"Delivery {delivery_id} set to {not delivery['scanned']}", 201
        else:
            return "The delivery could not be found", 404

    except:
        # Error while trying to update the resource
        return "Could not update the delivery", 500

# Create delivery function
@blueprint_deliveries.route('/', methods=['POST'])
def create_delivery():
    """
    Function that creates a new delivery object
    """

    # Get Request body from JSON
    request_data = request.json
    schema = DeliverySchema()  # Assign delivery schema

    try:
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
            # Validate request body against schema data types
            schema.load(request_data)

            # Add scanned and delivered flags
            body['scanned'] = False
            body['delivered'] = False

        except ValidationError as err:
            # Report validation error to the user
            return jsonify(err.messages), 400
        except:
            # Bad request as request body is not available
            return "Bad Request", 400        

        record_created = collection.insert_one(body)

        # Add courier service URL for this delivery
        recordUrl = CS_URL + f"/?id={record_created.inserted_id}"
        collection.update_one({"_id": record_created.inserted_id}, {"$set": {"url": recordUrl}})

        # Prepare the response
        if isinstance(record_created, list):
            # Return list of Id of newly created items
            return jsonify([str(v) for v in record_created]), 201
        else:
            # Return Id of newly created item
            return jsonify(str(record_created)), 201
    
    except:
        # Error while trying to create the resource
        return "Could not create a delivery", 500

