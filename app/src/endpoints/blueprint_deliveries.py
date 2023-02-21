"""Blueprint for deliveries endpoint"""

from config import client
from bson.json_util import dumps
from flask import Blueprint, jsonify, request
import json
import ast

# Define the blueprint
blueprint_deliveries = Blueprint(name="blueprint_deliveries", import_name=__name__)

# Select the database
db = client.inbox
# Select the collection
collection = db.deliveries

# Test endpoint
@blueprint_deliveries.route('/test', methods=['GET'])
def test():
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
        delivery_fetched = collection.find_one({ "deliveryId": delivery_id })
        print(collection)

        if delivery_fetched:
            return dumps(delivery_fetched)
        else:
            # No delivery was found
            return "No delivery was found", 404

    except:
        # Error while trying to fetch the delivery
        return "The delivery could not be fetched", 500

# Set scanned flag to true
@blueprint_deliveries.route('/<delivery_id>', methods=['PUT'])
def update_scanned(delivery_id):
    pass

# Create delivery function
@blueprint_deliveries.route('/', methods=['POST'])
def create_delivery():
    """
    Function that creates a new delivery object
    """

    try:
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as request body is not available
            return "Bad Request", 400
        
        record_created = collection.insert(body)

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

