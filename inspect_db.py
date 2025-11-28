from dotenv import load_dotenv
import firebase_admin

"""
Script to inspect database structure
"""

import os

from firebase_admin import credentials, db
import json

load_dotenv()

if not firebase_admin._apps:
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    db_url = os.environ.get("FIREBASE_DATABASE_URL")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {"databaseURL": db_url})

# Get all data
ref = db.reference("/")
data = ref.get()

print("\n=== Full Database Structure ===\n")
print(json.dumps(data, indent=2, default=str)[:2000])
print("\n... (truncated)")

# Check for artwall
if "artwall" in data:
    artwall_ref = db.reference("/artwall")
    artwall_data = artwall_ref.get()
    print("\n=== /artwall structure ===")
    print(f"Keys: {list(artwall_data.keys())}")

    if "posts" in artwall_data:
        print(f"\n/artwall/posts has {len(artwall_data['posts'])} items")
