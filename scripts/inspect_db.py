import os
import sys
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
    print("\n--- /posts analysis ---")
    posts_ref = db.reference("posts")
    try:
        posts_keys = posts_ref.get(shallow=True)
        if posts_keys:
            print(f"Total posts in /posts: {len(posts_keys)}")
            # Find post with url1
            # url_key placeholder removed; use actual fetched data when needed
            for k, v in posts_keys.items():
                # We need to fetch to check url1, so we can't just iterate keys
                # This is expensive. Let's try to fetch a batch.
                pass

            # Fetch last 50 and check
            print("Checking last 50 posts for url1...")
            batch = posts_ref.order_by_key().limit_to_last(50).get()
            # Find 'Plant people' post
            print("Searching for 'Plant people'...")
            # We have to scan because we can't query by title easily without an index
            # But we can just fetch a batch and look, or fetch all keys and look if title is in key (unlikely)
            # Let's fetch the last 100 posts, maybe it's recent?
            # Or just fetch all (shallow) and iterate? No, title is inside.

            # Let's try to find it in the artwall dump if we can't find it in posts easily
            # Actually, let's just fetch a larger batch of posts.
            batch = posts_ref.order_by_key().limit_to_last(300).get()
            found = False
            for k, v in batch.items():
                if v.get("title") == "Plant people":
                    print(f"Found 'Plant people' post: {k}")
                    print(f"coverImageUrl: {v.get('coverImageUrl')}")
                    print(f"url1: {v.get('url1')}")
                    found = True
                    break

            if not found:
                print("Could not find 'Plant people' in the last 300 posts.")

            sample_post = (
                {}
            )  # Dummy to prevent error below if we remove the previous block
            if "url1" in sample_post:
                print(f"url1: {sample_post['url1']}")
            if "coverImageUrl" in sample_post:
                print(f"coverImageUrl: {sample_post['coverImageUrl']}")
            if "medium" in sample_post:
                print(f"Medium field: {sample_post['medium']}")
        else:
            print("/posts is EMPTY or None")
    except Exception as e:
        print(f"Error reading /posts: {e}")
        # Fallback if shallow not supported
        posts_snapshot = posts_ref.order_by_key().limit_to_last(10).get()
        if posts_snapshot:
            print(f"Found {len(posts_snapshot)} posts (limit 10)")
            for k, v in posts_snapshot.items():
                print(f"Key: {k}")
                print(f"Medium: {v.get('medium', 'MISSING')}")
        else:
            print("/posts seems empty")

    # Check /artwall
    print("\n--- /artwall analysis ---")
    artwall_ref = db.reference("artwall")
    artwall_snapshot = artwall_ref.get()

    total_artwall = 0
    if artwall_snapshot:
        for medium, posts in artwall_snapshot.items():
            count = len(posts) if posts else 0
            print(f"  {medium}: {count}")
            total_artwall += count
    print(f"Total in /artwall: {total_artwall}")


if __name__ == "__main__":
    inspect_db()
