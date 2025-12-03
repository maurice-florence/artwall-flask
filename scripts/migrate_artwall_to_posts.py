import os
import sys
import time
from firebase_admin import credentials, db, initialize_app
from dotenv import load_dotenv

load_dotenv()

# Add app directory to path
sys.path.append(os.getcwd())


def migrate():
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
        pass

    print(f"Connected to {db_url}")

    # 1. Fetch all data from /artwall
    print("Fetching data from /artwall...")
    artwall_ref = db.reference("artwall")
    artwall_data = artwall_ref.get()

    if not artwall_data:
        print("No data in /artwall to migrate.")
        return

    posts_ref = db.reference("posts")

    count = 0
    updates = {}

    for medium, posts in artwall_data.items():
        print(f"Processing {medium} ({len(posts)} posts)...")
        for post_id, post_data in posts.items():
            if not isinstance(post_data, dict):
                continue

            # Prepare post data for /posts
            # 1. Inject medium
            post_data["medium"] = medium

            # 2. Ensure timestamp
            if "timestamp" not in post_data:
                if "recordCreationDate" in post_data:
                    post_data["timestamp"] = post_data["recordCreationDate"]
                else:
                    # Try to parse from key YYYYMMDD
                    try:
                        _ = post_id.split("_")[0]
                        # Simple approximation or just leave it
                        # We won't invent a timestamp if we can't find one,
                        # but the sorting logic relies on keys anyway.
                        pass
                    except Exception:
                        pass

            # 3. Add to updates
            # We use multi-path update for atomicity and speed
            updates[post_id] = post_data
            count += 1

            # Batch updates to avoid request too large
            if len(updates) >= 50:
                print(f"Writing batch of {len(updates)}...")
                posts_ref.update(updates)
                updates = {}
                time.sleep(0.1)  # Be nice to the database

    # Write remaining
    if updates:
        print(f"Writing final batch of {len(updates)}...")
        posts_ref.update(updates)

    print(f"Migration complete. Migrated {count} posts to /posts.")


if __name__ == "__main__":
    migrate()
