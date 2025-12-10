from flask import render_template, current_app
from app.blueprints.main.blueprint import main_bp
from app.services.firebase_service import get_paginated_posts, get_db_ref
from app.utils.post_helpers import group_posts_by_year
from app.utils.clean_content import clean_post_content


"""
Main Routes.
Handles the initial page load and displays the Masonry grid.
"""


@main_bp.route("/")
def index():
    """
    Renders the main page with the initial set of posts.
    Fetches the first 100 posts from Firebase, grouped by year.
    """
    try:
        # Initial load: Fetch 100 posts
        posts, next_cursor = get_paginated_posts(limit=100)
        current_app.logger.info(f"Loaded {len(posts)} posts from database")

        # Log medium distribution
        medium_counts = {}
        for post in posts:
            medium = post.get("medium", "unknown")
            medium_counts[medium] = medium_counts.get(medium, 0) + 1
        current_app.logger.info(f"Medium distribution: {medium_counts}")

        for post in posts:
            # Normalize score fields for consistent frontend rendering
            if "evaluationNum" not in post and "evaluation" in post:
                post["evaluationNum"] = post["evaluation"]
            if "ratingNum" not in post and "rating" in post:
                post["ratingNum"] = post["rating"]

            original = post.get("content", "")
            cleaned = clean_post_content(original) if original else ""
            post["cleaned_content"] = cleaned
            # Compose date string from day/month/year fields if present
            day = str(post.get("day", "")).zfill(2) if post.get("day") else ""
            month = str(post.get("month", "")).zfill(2) if post.get("month") else ""
            year = str(post.get("year", "")) if post.get("year") else ""
            if day and month and year:
                post["date_str"] = f"{year}-{month}-{day}"
            elif year and month:
                post["date_str"] = f"{year}-{month}"
            elif year:
                post["date_str"] = str(year)
            else:
                post["date_str"] = ""
            # Always set subcategory from subtype if present
            subcat = post.get("subtype", "")
            # For writing, fallback if subtype is missing
            if not subcat and post.get("medium", "").lower() == "writing":
                tags = post.get("tags", [])
                if isinstance(tags, list) and any("poetry" in t.lower() for t in tags):
                    subcat = "Poetry"
                elif "poetry" in (post.get("title", "").lower()):
                    subcat = "Poetry"
                else:
                    subcat = "Poetry"  # Default for writing if nothing else
            post["subcategory"] = subcat
            # Ensure numeric fields are 0 if missing, for Jinja/JSON consistency
            if "evaluationNum" not in post:
                post["evaluationNum"] = 0
            if "ratingNum" not in post:
                post["ratingNum"] = 0

        # Group posts by year for display with separators
        grouped_posts = group_posts_by_year(posts)

        return render_template(
            "index.html", grouped_posts=grouped_posts, next_cursor=next_cursor
        )
    except Exception as e:
        return render_template(
            "index.html", grouped_posts=[], next_cursor=None, error=str(e)
        )


@main_bp.route("/post/<post_id>")
def post_detail(post_id):
    """
    Show detailed view of a single post.
    """
    try:
        # Try to find the post in all medium types
        medium_types = ["audio", "drawing", "sculpture", "writing"]
        post = None

        for medium in medium_types:
            ref = get_db_ref(f"artwall/{medium}/{post_id}")
            data = ref.get()  # type: ignore[misc]
            if data:
                post = data
                post["id"] = post_id
                post["medium"] = medium
                break

        if not post:
            return render_template("errors/404.html"), 404

        return render_template("post_detail.html", post=post)
    except Exception as e:
        current_app.logger.error(f"Error loading post {post_id}: {str(e)}")
        return render_template("errors/404.html"), 404


@main_bp.route("/about")
def about():
    """About page."""
    return render_template("about.html")
