import os  # Import os at the top of the file

# Set the Google Application Credentials environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/serviceAccountKey.json"

from flask import Flask
from google.cloud import firestore  # Import Firestore after setting the environment variable

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "samuel is great sdsdsdsd"

    from .views import views
    from .auth import auth
    from  .shopping import shopping
    from  .whatsapp import whatsapp

    # Register blueprints
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(shopping, url_prefix="/")
    app.register_blueprint(whatsapp, url_prefix="/")

    return app
