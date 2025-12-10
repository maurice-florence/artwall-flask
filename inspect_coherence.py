from app.services.firebase_service import get_db_ref
from flask import Flask

app = Flask(__name__)


def inspect_coherence():
    # Attempt to find "Coherence" or list titles to find ID
    ref = get_db_ref("artwall/writing")
    data = ref.get()

    found_id = None
    for key, val in data.items():
        if "coherence" in val.get("title", "").lower():
            found_id = key
            print(f"Found Coherence ID: {key}")
            print(f"Data: {val}")
            break

    if not found_id:
        print("Coherence not found in writing.")


if __name__ == "__main__":
    inspect_coherence()
