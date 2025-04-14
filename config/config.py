import os

class Config:
    # Path to the Firestore service account key file
    FIREBASE_CREDENTIALS = os.path.join(os.path.dirname(__file__), "db-ecom-01-firebase-adminsdk-7ltdr-6e033444d6.json")
    FIRESTORE_COLLECTION = "your_collection_name"  # Replace with your Firestore collection name
