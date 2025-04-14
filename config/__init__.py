from flask import Flask
from google.cloud import firestore
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Firestore client
    app.firestore_client = firestore.Client.from_service_account_json(app.config['FIREBASE_CREDENTIALS'])

    return app
