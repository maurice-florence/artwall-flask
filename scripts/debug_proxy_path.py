import os
import sys
from firebase_admin import credentials, storage, initialize_app
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.getcwd())


def debug_proxy_path():
    # Initialize Firebase
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    db_url = os.environ.get("FIREBASE_DATABASE_URL")
    storage_bucket = os.environ.get("FIREBASE_STORAGE_BUCKET")

    if storage_bucket and storage_bucket.startswith("gs://"):
        storage_bucket = storage_bucket.replace("gs://", "")

    print(f"Using bucket: {storage_bucket}")

    try:
        cred = credentials.Certificate(cred_path)
        initialize_app(cred, {"databaseURL": db_url, "storageBucket": storage_bucket})
    except ValueError:
        pass

    bucket = storage.bucket(name=storage_bucket)

    # The path we are trying to access (from browser logs)
    target_path = "drawing/20250608_drawing_marker_alien-1_01.jpg"
    print(f"\nChecking target path: {target_path}")

    blob = bucket.blob(target_path)
    if blob.exists():
        print("SUCCESS: Blob exists at target path.")
    else:
        print("FAILURE: Blob does NOT exist at target path.")

        # List files in the 'drawing' directory to see what's there
        print("\nListing files in 'drawing/' prefix:")
        blobs = bucket.list_blobs(prefix="drawing/")
        count = 0
        for b in blobs:
            print(f" - {b.name}")
            count += 1
            if count >= 10:
                print(" ... (more)")
                break
        if count == 0:
            print("No blobs found in 'drawing/' prefix.")


if __name__ == "__main__":
    debug_proxy_path()
