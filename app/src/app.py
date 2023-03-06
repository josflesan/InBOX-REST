"""Flask Application"""

# Load libraries
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit
from config import Config

# Load modules
from src.endpoints.blueprint_deliveries import blueprint_deliveries
from src.endpoints.blueprint_users import blueprint_users
from src.endpoints.blueprint_register import blueprint_register  #TODO: probably delete this

# Initialize Flask app
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Set up config
app.config["SECRET_KEY"] = Config.SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ACCESS_TOKEN_EXPIRES
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
app.config['CORS_HEADERS'] = Config.JWT_SECRET_KEY

# Register blueprints, ensuring paths are versioned
app.register_blueprint(blueprint_deliveries, url_prefix="/api/v1/deliveries")
app.register_blueprint(blueprint_users, url_prefix="/api/v1/users")
app.register_blueprint(blueprint_register, url_prefix="/api/v1/")  #TODO: probably delete this