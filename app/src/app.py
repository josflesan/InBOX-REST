"""Flask Application"""

# Load libraries
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit
from flask_bcrypt import Bcrypt
from flask_praetorian import Praetorian
from config import Config

# Load modules
from src.endpoints.blueprint_deliveries import blueprint_deliveries
from src.endpoints.blueprint_users import blueprint_users
from src.endpoints.blueprint_register import blueprint_register  #TODO: probably delete this

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)  #TODO: likely change this
cors = CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register blueprints, ensuring paths are versioned
app.register_blueprint(blueprint_deliveries, url_prefix="/api/v1/deliveries")
app.register_blueprint(blueprint_users, url_prefix="/api/v1/users")
app.register_blueprint(blueprint_register, url_prefix="/api/v1/")  #TODO: probably delete this