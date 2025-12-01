"""
API Routes.
Handles HTMX requests for dynamic content (load more, etc.).
Returns HTML fragments, not JSON.
"""

from flask import request, render_template, current_app, jsonify
import os
from app.blueprints.api.blueprint import api_bp
from app.services.firebase_service import get_paginated_posts
from app.utils.post_helpers import group_posts_by_year
from app.extensions import csrf
from app.services.firebase_service import update_post as fb_update_post


@api_bp.route("/load-more")
def load_more():
    """
    HTMX endpoint for loading more posts.
    Returns HTML fragments to be appended to the grid.

    Query Parameters:
        cursor: The index/offset of the last post from the previous page
    """
    cursor = request.args.get("cursor")
    current_app.logger.debug(f"Load more requested with cursor: {cursor}")

    if not cursor:
        return "No cursor provided", 400

    try:
        # Convert cursor to integer (it's now an index/offset)
        cursor_value = int(cursor)

        # Fetch next 100 posts starting after the cursor
        posts, next_cursor = get_paginated_posts(limit=100, end_at=cursor_value)

        current_app.logger.debug(
            f"Loaded {len(posts)} posts, next cursor: {next_cursor}"
        )

        # Group posts by year
        grouped_posts = group_posts_by_year(posts)

        # Return ONLY the grid items partial, not the full page
        return render_template(
            "partials/grid_items.html",
            grouped_posts=grouped_posts,
            next_cursor=next_cursor,
        )
    except ValueError:
        return "Invalid cursor format", 400
    except Exception as e:
        current_app.logger.error(f"Error loading more posts: {str(e)}")
        return f"Error: {str(e)}", 500


@api_bp.route("/search")
def search():
    """
    HTMX endpoint for searching posts.
    Returns filtered HTML fragments.
    """
    query = request.args.get("q", "")

    if not query:
        return render_template("partials/grid_items.html", posts=[], next_cursor=None)

    try:
        # TODO: Implement search functionality in firebase_service
        # For now, return empty results
        return render_template("partials/grid_items.html", posts=[], next_cursor=None)
    except Exception as e:
        current_app.logger.error(f"Error searching posts: {str(e)}")
        return f"Error: {str(e)}", 500


@api_bp.route("/client-log", methods=["POST"])
@csrf.exempt
def client_log():
    """
    Receive client-side debug logs and print them to server logs.
    This helps diagnose front-end flip/mirroring behavior from the server terminal.
    """
    try:
        data = request.get_json(silent=True) or {}
        # Only emit logs when explicitly enabled
        if os.getenv("APP_CLIENT_LOG_DEBUG", "0").lower() in ("1", "true", "yes"):
            event = data.get("event")
            post_id = data.get("postId")
            details = {k: v for k, v in data.items() if k not in ("event", "postId")}
            current_app.logger.debug(
                f"[CLIENT-LOG] event={event} post_id={post_id} details={details}"
            )
        return jsonify(status="ok"), 204
    except Exception as e:
        current_app.logger.error(f"Error in client_log: {e}")
        return jsonify(error=str(e)), 500


@api_bp.route("/post/<post_id>/evaluation", methods=["POST"])
@csrf.exempt
def update_evaluation(post_id):
    """Update personal evaluation (1-5 stars) for a post."""
    try:
        data = request.get_json(silent=True) or {}
        value = int(data.get("value", 0))
        if value < 1 or value > 5:
            return jsonify(error="Invalid evaluation value"), 400
        fb_update_post(post_id, {"evaluationNum": value})
        return jsonify(status="ok", evaluationNum=value)
    except Exception as e:
        current_app.logger.error(f"Error updating evaluation: {e}")
        return jsonify(error=str(e)), 500


@api_bp.route("/post/<post_id>/rating", methods=["POST"])
@csrf.exempt
def update_rating(post_id):
    """Update audience rating (1-5 stars) for a post. Overwrites for now."""
    try:
        data = request.get_json(silent=True) or {}
        value = int(data.get("value", 0))
        if value < 1 or value > 5:
            return jsonify(error="Invalid rating value"), 400
        fb_update_post(post_id, {"ratingNum": value})
        return jsonify(status="ok", ratingNum=value)
    except Exception as e:
        current_app.logger.error(f"Error updating rating: {e}")
        return jsonify(error=str(e)), 500
