"""Blueprint for deliveries endpoint"""

from config import Config
from src.decorators.access_control import AccessControl
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_socketio import emit
from marshmallow import Schema, fields, ValidationError
import json, time, ast

# deliveries endpoints schema
class DeliverySchema(Schema):
    hashCode = fields.String(required=True)
    userId = fields.String(required=True)
    email = fields.String(required=False)
    username = fields.String(required=False)

# Define the blueprint
blueprint_deliveries = Blueprint(name="blueprint_deliveries", import_name=__name__)

# Select the database
db = Config.DATABASE_CLIENT.inbox
# Select the collection
collection = db.deliveries

# Test endpoint
@blueprint_deliveries.route('/test', methods=['GET'])
@cross_origin()
def test():
    """
    Test endpoint to ping REST-API
    """
    output = {"msg": "I'm the test endpoint from blueprint_deliveries"}
    return jsonify(output)

# Get delivery function
@blueprint_deliveries.route('/<delivery_id>', methods=['GET'])
@cross_origin()
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
            return "No delivery was not found", 404

    except Exception as err:
        # Error while trying to fetch the delivery
        return jsonify({"err": f"Internal Server Error: {err}"}), 500

# Verify hash value
@blueprint_deliveries.route('/<delivery_id>/<hash_code>', methods=['GET'])
@cross_origin()
def check_hash(delivery_id, hash_code):
    """
    Function that checks whether a hash code matches with a given delivery
    """

    try:
        delivery = collection.find_one({"_id": ObjectId(delivery_id)})

        if delivery['hashCode'] == hash_code:
            # Update scanned flags
            collection.update_one({"_id": ObjectId(delivery_id)}, {"$set": {"scanned": True}})
            return jsonify({"result": True}), 201

        return jsonify({"result": False}), 201

    except:
        # The delivery could not be retrieved
        return jsonify({"err": f"The delivery with id {delivery_id} could not be found"}), 401


# Toggle scanned value
@blueprint_deliveries.route('/<delivery_id>', methods=['PUT'])
@cross_origin()
def toggle_scanned(delivery_id):
    """
    Function that updates the scanned flag of a delivery record (true/false)
    """

    try:
        delivery = collection.find_one({"_id": ObjectId(delivery_id)})
        update = collection.update_one({"_id": ObjectId(delivery_id)}, {"$set": { "scanned": True }})

        if update:
            return f"Delivery {delivery_id} set to {not delivery['scanned']}", 201
        else:
            return "The delivery could not be found", 404

    except:
        # Error while trying to update the resource
        return "Could not update the delivery", 500

# Long Poll call for navigation in courier-service
@blueprint_deliveries.route('/<delivery_id>/poll', methods=['GET'])
@cross_origin()
def poll_scanned(delivery_id):
    """
    Function to long poll the scanned flag in the record
    """

    try:
        # Poll the database
        while True:
            time.sleep(0.5)
            scannedValue = collection.find_one({"_id": ObjectId(delivery_id)})['scanned']

            if scannedValue:
                # emit(jsonify("scanned", {"result": scannedValue}))
                return jsonify({"result": "Scanned"}), 201

    except:
        # Error while trying to poll the database
        return "Polling failed", 500

# Endpoint to update delivered status
@blueprint_deliveries.route('/<delivery_id>/delivered', methods=['GET'])
@cross_origin()
def update_delived(delivery_id):
    """
    Function that updates the delivered status on a delivery
    """

    try:
        # Update the delivery flag
        collection.update_one({"_id": ObjectId(delivery_id)}, {"$set": {"delivered": True}})
        return jsonify({"result": True}), 201

    except:
        # The delivery could not be obtained or updated
        return "The delivery was not found", 500

# Upload image endpoint
@blueprint_deliveries.route('/<delivery_id>/image', methods=['POST'])
@cross_origin()
def upload_image(delivery_id):
    """
    Function that uploads image from byte array to MongoDB
    """

    try:
        # Get base 64 string from request data
        body = ast.literal_eval(json.dumps(request.get_json()))
        base64Image = body['base64Image']

        # Upload base64 image to the database
        collection.update_one({"_id": ObjectId(delivery_id)}, {"$set" : {"imageProof": base64Image}})
        return jsonify({"result": True}), 201

    except:
        # The image could not be uploaded
        return jsonify({"result": False}), 500

# Retrieve image endpoint
@blueprint_deliveries.route('/image/<delivery_id>', methods=["POST"])
@cross_origin()
@AccessControl.is_self_or_admin
def get_image(delivery_id):
    """
    Function to obtain the base64 image of the delivery proof photo submitted
    """

    try:
        # Try obtaining the delivery specified
        delivery = collection.find_one({"_id": ObjectId(delivery_id)})

        # If a delivery image proof exists, return it
        if 'imageProof' in delivery:
            return jsonify({"result": delivery["imageProof"]}), 201

        # Otherwise, fail gracefully
        return jsonify({"err": f"The image proof could not be obtained"}), 201

    except Exception as err:
        # If any error occurs, fail
        return jsonify({"err": f"Internal Server Error: {err}"}), 500

# Create delivery function
@blueprint_deliveries.route('/create', methods=['POST'])
@cross_origin()
@AccessControl.is_self_or_admin
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
            return jsonify({"err": f"{err.messages}"}), 400
        except Exception as err:
            # Bad request as request body is not available
            return jsonify({"err": f"Internal Server Error: {err}"}), 400

        record_created = collection.insert_one(body)

        # Add courier service URL for this delivery
        recordUrl = Config.CS_URL + f"?id={record_created.inserted_id}"
        collection.update_one({"_id": record_created.inserted_id}, {"$set": {"url": recordUrl}})

        # Prepare the response
        if isinstance(record_created, list):
            # Return list of Id of newly created items
            return jsonify({str(k): str(v)  for k, v in record_created.items()}), 201
        else:
            # Return Id of newly created item
            return jsonify({"result": str(record_created)}), 201
    
    except Exception as err:
        # Error while trying to create the resource
        return jsonify({"err": f"Could not create the delivery: {err}"}), 500


# Delete delivery function
@blueprint_deliveries.route('/delete/<delivery_id>', methods=["DELETE"])
@cross_origin()
@AccessControl.is_self_or_admin
def delete_delivery(delivery_id):
    """
    Function that deletes a delivery from the database
    """

    try:
        delivery = collection.find_one({"_id": ObjectId(delivery_id)})

        # Ensure that delivery has been scanned and delivered
        if not (delivery['scanned'] and delivery['delivered']):
            return jsonify({"result": False}), 201

        # Delete afterwards
        collection.delete_one({"_id": ObjectId(delivery_id)})

        return jsonify({"result": True}), 201

    except:
        return "The delivery could not be deleted", 500

