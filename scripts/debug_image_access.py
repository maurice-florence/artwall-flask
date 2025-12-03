import os
import sys
from firebase_admin import credentials, storage, initialize_app, db
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.getcwd())


def debug_image_access():
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

    # 1. Find the Alien 1 post
    print("Searching for 'Alien 1' post...")
    ref = db.reference("posts")
    # Fetch a batch
    batch = ref.order_by_key().limit_to_last(100).get()

    target_post = None

    for k, v in batch.items():
        if "Alien 1" in v.get("title", ""):
            target_post = v
            print(f"Found post: {k} - {v.get('title')}")
            break

    if not target_post:
        print("Could not find 'Alien 1' post.")
        return

    original_url = target_post.get("coverImageUrl")
    print(f"Original URL: {original_url}")

    if not original_url:
        print("No coverImageUrl found.")
        return

    # 2. Generate Signed URL
    print("\nGenerating Signed URL...")

    # Logic from firebase_service.py
    prefix = f"https://storage.googleapis.com/{storage_bucket}/"
    if original_url.startswith(prefix):
            start_idx = len(prefix)
            blob_path = original_url[start_idx:]
        print(f"Blob path: {blob_path}")

        bucket = storage.bucket(storage_bucket)
        blob = bucket.blob(blob_path)

        try:
            # 3. Test Metadata / Tokens
            print("\nTesting metadata access...")
            blob.reload()
            print(f"Metadata: {blob.metadata}")

            # Check for download tokens (custom metadata or specific field)
            # The python client might hide it, or it's in .metadata
            # Actually, for firebase-admin, it's often not exposed directly in standard GCS client
            # But let's check.

            # Construct Firebase-style URL if token exists
            # We might need to make a patch request to create a token if one doesn't exist?
            # Or just use generating signed URL with V2?

        except Exception as e:
            print(f"Error getting metadata: {e}")

    else:
        print(f"URL does not match prefix {prefix}")


if __name__ == "__main__":
    debug_image_access()
