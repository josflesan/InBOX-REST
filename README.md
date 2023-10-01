# InBoX-REST
Python Flask REST API that wraps around MongoDB backend to enable communication between database and services (app, courier-service and Raspberry Pi).

# Endpoints

The REST API endpoints are broadly divided into 3 categories (blueprints): Registration, Users and Deliveries

### 1. Registration

The registration endpoints are used to securely provide a new API Key to authorized users for the API's private endpoints.

- `POST /login`: used to register a new device and API key for private endpoints

### 2. Users

User endpoints are used to authenticate, login and manage application users in the database.

- `POST /login`: used to log in an existing user into the application via JWT
- `GET /logout`: logs out the current user
- `GET /<email>/verification`: used to send a verification code to user for 2FA
- `POST/PUT /query`: used to retrieve or update a single user in the database
- `POST /register`: creates a new user in the database from the request body data
- `GET /twofactor/<email>/<code>`: used to resolve a 2FA prompt (can only be called with valid API key)
- `GET /elevate/<email>`: used to elevate a user's privileges (can only be called by admin user)
- `DELETE /delete`: used to delete a user from the database

### 3. Deliveries

Deliveries endpoints are used to perform CRUD operations on database delivery entries.

- `GET /<delivery_id>`: retrieves a single delivery record
- `GET /<delivery_id>/<hash_code>`: checks whether a hash code matches with a given delivery
- `PUT /<delivery_id>`: updates the scanned flag of a delivery record
- `GET /<delivery_id>/poll`: long polls the scanned flag in the record
- `GET /<delivery_id>/delivered`: updates the delivered status on a delivery
- `POST /<delivery_id>/image`: uploads an image from byte array to database (for in-app delivery proof)
- `POST /image/<delivery_id>`: obtains the base64 image of the delivery proof photo submitted
- `POST /create`: creates a new delivery object in the database
- `DELETE /delete/<delivery_id>`: deletes a delivery from the database

# Usage

The app relies on a local (self-hosted) instance of the MongoDB database to be running. Once this is set up, the scripts can be used to spin up the API (`./run-dev.sh` and `./run-prod.sh`)

**This repository is part of System Design Project 2023 (associated with University of Edinburgh)**
