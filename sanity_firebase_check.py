# sanity_firebase_check.py: Minimal integration test for Firebase endpoint
import os
import requests

# Use test credentials and endpoint
FIREBASE_URL = os.environ.get('FIREBASE_DATABASE_URL')
if not FIREBASE_URL:
    print('[WARN] FIREBASE_DATABASE_URL not set')
    exit(0)

try:
    # Try to hit a known endpoint (e.g., /artwall)
    url = FIREBASE_URL.rstrip('/') + '/artwall.json'
    resp = requests.get(url, timeout=5)
    if resp.status_code == 200:
        print('[OK] Firebase endpoint reachable')
    else:
        print(f'[FAIL] Firebase endpoint returned status {resp.status_code}')
        exit(1)
except Exception as e:
    print(f'[FAIL] Firebase integration error: {e}')
    exit(1)
