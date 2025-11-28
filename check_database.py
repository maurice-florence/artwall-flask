import time

"""
Script to check Firebase database content and add test data if empty
"""

import os

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# Load environment variables
load_dotenv()


def check_database():
    """Check database content"""
    print("\n=== Checking Firebase Database ===\n")

    # Initialize Firebase if not already done
    if not firebase_admin._apps:
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        db_url = os.environ.get("FIREBASE_DATABASE_URL")

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {"databaseURL": db_url})
        print("✓ Firebase initialized\n")

    # Check root structure
    ref = db.reference("/")
    data = ref.get()  # type: ignore[misc]

    if data is None:
        print("⚠ Database is completely empty")
        return None

    if not isinstance(data, dict):
        print("⚠ Unexpected data type")
        return None

    print(f"Database root keys: {list(data.keys())}\n")

    # Check posts
    posts_ref = db.reference("/posts")
    posts = posts_ref.get()  # type: ignore[misc]

    if posts is None:
        print("⚠ /posts path is empty")
        return None

    if not isinstance(posts, dict):
        print("⚠ Unexpected posts data type")
        return None

    print(f"Found {len(posts)} posts in database:")

    # Show first few posts
    post_items = list(posts.items())[:5]
    for post_id, post_data in post_items:
        print(f"  - {post_id}: {post_data.get('title', 'No title')[:50]}")  # noqa: E501

    if len(posts) > 5:
        print(f"  ... and {len(posts) - 5} more")

    return posts


def add_test_data():
    """Add test posts to database"""
    print("\n=== Adding Test Data ===\n")

    posts_ref = db.reference("/posts")

    test_posts = [
        {
            "title": "Welcome to Artwall",
            "content": "<p>This is your creative archive. Import your Evernote notes to get started!</p>",
            "timestamp": int(time.time() * 1000),
            "author": "System",
            "tags": ["welcome", "getting-started"],
        },
        {
            "title": "Getting Started Guide",
            "content": (
                '<p>To import your notes, click the "Import ENEX File" button and '
                "select your exported Evernote file.</p>"
            ),
            "timestamp": int(time.time() * 1000) - 1000,
            "author": "System",
            "tags": ["guide", "tutorial"],
        },
        {
            "title": "Sample Creative Note",
            "content": (
                "<p>Your creative ideas, sketches, and notes will appear here in a "
                "beautiful masonry grid layout.</p>"
            ),
            "timestamp": int(time.time() * 1000) - 2000,
            "author": "System",
            "tags": ["sample", "creative"],
        },
    ]

    for i, post in enumerate(test_posts, 1):
        new_post_ref = posts_ref.push(post)  # type: ignore[arg-type]
        print(f"✓ Added test post {i}: {post['title']} (ID: {new_post_ref.key})")

    print(f"\n✓ Successfully added {len(test_posts)} test posts")


def main():
    """Main function"""
    try:
        posts = check_database()

        if posts is None:
            response = input("\n❓ Database is empty. Add test data? (y/n): ")
            if response.lower() == "y":
                add_test_data()
                print("\n✅ Test data added. Refresh your browser to see the posts.")
            else:
                print("\n💡 Import an ENEX file from the web interface to add posts.")
        else:
            print(f"\n✅ Database has data. Showing {len(posts)} posts.")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
