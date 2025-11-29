import os
import requests
import firebase_admin
from firebase_admin import credentials, db, storage


def test_flask_app():
    url = os.environ.get("CLOUD_RUN_URL")  # Set this env var to your deployed URL
    if not url:
        print("CLOUD_RUN_URL environment variable not set.")
        return False
    try:
        resp = requests.get(url)
        print(f"Flask app status code: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Error connecting to Flask app: {e}")
        return False


def test_firebase_connection():
    try:
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not cred_path or not os.path.exists(cred_path):
            print("Service account file not found.")
            return False
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
                "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
            },
        )
        # Test database read
        ref = db.reference("/")
        data = ref.get()
        if isinstance(data, dict):
            print("Database connection successful. Root keys:", list(data.keys()))
        else:
            print("Database connection successful. Data:", data)
        # Test storage
        bucket = storage.bucket()
        blobs = list(bucket.list_blobs(max_results=1))
        print("Storage connection successful. Found blobs:", len(blobs))
        return True
    except Exception as e:
        print(f"Firebase connection error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Flask app deployment...")
    flask_ok = test_flask_app()
    print("Testing Firebase connection...")
    firebase_ok = test_firebase_connection()
    if flask_ok and firebase_ok:
        print("✅ Deployment and setup look good!")
    else:
        print("❌ There are issues with the deployment or setup.")
