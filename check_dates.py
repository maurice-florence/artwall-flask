"""
Script to check date structure in Firebase posts
"""

import os


from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# Load environment variables
load_dotenv()


def check_dates():
    """Check date structure in posts"""
    print("\n=== Checking Date Structure ===\n")

    # Initialize Firebase
    if not firebase_admin._apps:
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        db_url = os.environ.get("FIREBASE_DATABASE_URL")

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {"databaseURL": db_url})

    medium_types = ["audio", "drawing", "sculpture", "writing"]

    for medium in medium_types:
        print(f"\n{medium.upper()}")
        print("=" * 80)

        ref = db.reference(f"/artwall/{medium}")
        all_posts = ref.get()  # type: ignore[misc]

        # Get first 3 posts
        posts = {}
        if all_posts and isinstance(all_posts, dict):
            for i, (post_id, post_data) in enumerate(all_posts.items()):
                if i >= 3:
                    break
                posts[post_id] = post_data

        if posts and isinstance(posts, dict):
            for post_id, post_data in posts.items():
                print(f"\nPost ID: {post_id}")
                print(f"Title: {post_data.get('title', 'No title')}")

                # Check all date-related fields
                year = post_data.get("year")
                month = post_data.get("month")
                day = post_data.get("day")
                timestamp = post_data.get("timestamp")
                record_date = post_data.get("recordCreationDate")

                print(f"  year field: {year}")
                print(f"  month field: {month}")
                print(f"  day field: {day}")
                print(f"  timestamp field: {timestamp}")
                print(f"  recordCreationDate field: {record_date}")

                # Try to parse recordCreationDate
                if record_date:
                    try:
                        ts = (
                            record_date / 1000
                            if record_date > 10000000000
                            else record_date
                        )
                        dt = datetime.fromtimestamp(ts)
                        print(
                            f"  recordCreationDate parsed: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                    except Exception as e:
                        print(f"  recordCreationDate parsing failed: {e}")

                # Try to parse timestamp
                if timestamp:
                    try:
                        ts = timestamp / 1000 if timestamp > 10000000000 else timestamp
                        dt = datetime.fromtimestamp(ts)
                        print(f"  timestamp parsed: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    except Exception as e:
                        print(f"  timestamp parsing failed: {e}")

                print("-" * 80)


if __name__ == "__main__":
    check_dates()
