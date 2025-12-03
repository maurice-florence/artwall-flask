import os
import sys
import json
from firebase_admin import credentials, db, initialize_app
from dotenv import load_dotenv

load_dotenv()

# Add app directory to path
sys.path.append(os.getcwd())


def inspect_db():
    # Initialize Firebase
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    db_url = os.environ.get("FIREBASE_DATABASE_URL")

    if not cred_path or not db_url:
        print("Missing credentials or DB URL")
        return

    try:
        cred = credentials.Certificate(cred_path)
        initialize_app(cred, {"databaseURL": db_url})
    except ValueError:
        # Already initialized
        pass

    print(f"Connected to {db_url}")

    # Check /posts
    print("\n--- /posts structure (first 1) ---")
    posts_ref = db.reference("posts")
    posts_snapshot = posts_ref.order_by_key().limit_to_first(1).get()
    if posts_snapshot:
        print(json.dumps(posts_snapshot, indent=2))
    else:
        print("No posts found in /posts")

    # Check /artwall
    print("\n--- /artwall structure ---")
    artwall_ref = db.reference("artwall")
    artwall_snapshot = artwall_ref.get()
    print(f"Keys in /artwall: {artwall_snapshot}")

    if artwall_snapshot:
        for key in artwall_snapshot:
            print(f"\n--- /artwall/{key} (first 1) ---")
            medium_ref = db.reference(f"artwall/{key}")
            medium_snapshot = medium_ref.order_by_key().limit_to_first(1).get()
            if medium_snapshot:
                print(json.dumps(medium_snapshot, indent=2))
            else:
                print(f"No items in /artwall/{key}")


if __name__ == "__main__":
    inspect_db()
