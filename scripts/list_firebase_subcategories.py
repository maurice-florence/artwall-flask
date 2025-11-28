"""
Script to list all unique subcategories for each medium in the Firebase artwall database.
Usage: Run with the correct Firebase credentials and database URL set.
"""


import firebase_admin
from firebase_admin import credentials, db
import os

# Path to your Firebase service account key
CRED_PATH = os.path.join(os.path.dirname(__file__), '..', 'firebase-service-account.json')
# Your Firebase Realtime Database URL
DB_URL = 'https://artwall-by-jr-default-rtdb.europe-west1.firebasedatabase.app/'

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(CRED_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DB_URL
    })



# Explicitly look in medium folders under /artwall
medium_types = ['audio', 'drawing', 'sculpture', 'writing']
subcategories = {}
ref = db.reference('artwall')
artwall = ref.get()

if artwall and isinstance(artwall, dict):
    for medium in medium_types:
        posts = artwall.get(medium)
        if not posts or not isinstance(posts, dict):
            subcategories[medium] = []
            continue
        subcat_set = set()
        for post_id, post in posts.items():
            if not isinstance(post, dict):
                continue
            subcat = post.get('subtype')
            if subcat:
                subcat_set.add(subcat.strip())
        subcategories[medium] = sorted(subcat_set)
else:
    print("Warning: /artwall is not a dictionary or is empty. No results.")

print("Subcategories by medium:")
for medium, subcats in subcategories.items():
    print(f"{medium}: {sorted(subcats)}")
