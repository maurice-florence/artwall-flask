from collections import Counter
from app import create_app

from app.services.firebase_service import get_paginated_posts, init_firebase


def test_pagination():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    init_firebase(app)

    all_posts = []
    cursor = None
    page = 0

    while True:
        page += 1
        posts, cursor = get_paginated_posts(limit=50, end_at=cursor)
        all_posts.extend(posts)
        print(f"Page {page}: {len(posts)} posts, cursor: {cursor}")
        if not cursor:
            break

    counts = Counter([p["medium"] for p in all_posts])
    print(f"\nTotal: {len(all_posts)} posts")
    print(f"Final mediums: {dict(counts)}")


if __name__ == "__main__":
    test_pagination()
