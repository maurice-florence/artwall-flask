"""
Firebase Service Module.
Wraps Firebase Admin SDK for database operations and cursor-based pagination.
"""

import firebase_admin
from firebase_admin import credentials, db
from flask import current_app
import time
from typing import List, Dict, Tuple, Optional
import json

# Global reference to Firebase database
_firebase_db = None


def init_firebase(app):
    """
    Initialize Firebase Admin SDK.
    Called once during app creation in __init__.py.

    Args:
        app: Flask application instance
    """
    global _firebase_db

    import os
    import logging

    logger = logging.getLogger(__name__)

    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        firebase_config_json = os.environ.get("FIREBASE_CONFIG")
        db_url = os.environ.get("FIREBASE_DATABASE_URL") or app.config.get(
            "FIREBASE_DATABASE_URL"
        )

        if firebase_config_json:
            logger.debug(
                "Initializing Firebase from FIREBASE_CONFIG environment variable."
            )
            try:
                cred = credentials.Certificate(json.loads(firebase_config_json))
                firebase_admin.initialize_app(cred, {"databaseURL": db_url})
                app.logger.debug(
                    "Firebase Admin SDK initialized from FIREBASE_CONFIG env var."
                )
            except Exception as e:
                logger.error(
                    f"Error initializing Firebase from FIREBASE_CONFIG: {e}",
                    exc_info=True,
                )
                app.logger.error(
                    f"Failed to initialize Firebase from FIREBASE_CONFIG: {str(e)}"
                )
                raise
        else:
            cred_path = app.config.get("FIREBASE_CREDENTIALS_PATH")
            logger.debug(f"FIREBASE_CREDENTIALS_PATH: {cred_path}")
            if not cred_path:
                app.logger.warning(
                    "FIREBASE_CREDENTIALS_PATH not set. Firebase will not be initialized."
                )
                return
            if os.path.exists(cred_path):
                logger.debug(f"File exists at: {cred_path}")
                if os.access(cred_path, os.R_OK):
                    logger.debug(f"File is readable at: {cred_path}")
                    try:
                        cred = credentials.Certificate(cred_path)
                        firebase_admin.initialize_app(cred, {"databaseURL": db_url})
                        app.logger.debug(
                            "Firebase Admin SDK initialized successfully from file."
                        )
                    except Exception as e:
                        logger.error(f"Error initializing Firebase: {e}", exc_info=True)
                        app.logger.error(f"Failed to initialize Firebase: {str(e)}")
                        raise
                else:
                    logger.error(f"File exists but is NOT readable at: {cred_path}")
                    app.logger.error(f"File exists but is NOT readable at: {cred_path}")
            else:
                logger.error(f"File does NOT exist at: {cred_path}")
                app.logger.error(f"File does NOT exist at: {cred_path}")

    _firebase_db = db


def get_db_ref(path: str):
    """
    Get a Firebase database reference.

    Args:
        path: Database path (e.g., 'posts', 'users/uid')

    Returns:
        Firebase database reference
    """
    if _firebase_db is None:
        raise RuntimeError("Firebase has not been initialized")
    return _firebase_db.reference(path)


def get_paginated_posts(
    limit: int = 20, end_at: Optional[str] = None
) -> Tuple[List[Dict], Optional[str]]:
    """
    Fetch paginated posts using cursor-based pagination from /posts.
    Uses Firebase's limit_to_last for reverse chronological order (newest first).

    Args:
        limit: Number of posts to fetch
        end_at: Cursor (post ID/key) to end at (inclusive) for pagination.
                In reverse order, this acts as the "start" for the next page.

    Returns:
        Tuple of (posts_list, next_cursor)
        - posts_list: List of post dictionaries with 'id' added
        - next_cursor: The ID of the last post in this batch (to be used as end_at for next page),
                       or None if no more posts.
    """
    try:
        ref = get_db_ref("posts")

        # We want newest first, so we order by key (which is date-based).
        query = ref.order_by_key()

        # If a cursor is provided, we end at that cursor (inclusive).
        # Since we are traversing backwards (newest to oldest), 'end_at' in Firebase
        # means "values less than or equal to".
        if end_at:
            query = query.end_at(end_at)

        # Fetch limit + 1 to check if there is a next page
        # limit_to_last gives us the "largest" keys (newest dates)
        posts_data = query.limit_to_last(limit + 1).get()

        if not posts_data:
            return [], None

        # Check if we fetched a full batch (potential for more pages)
        fetched_count = len(posts_data)
        has_more_possible = fetched_count == limit + 1

        # Convert dict to list of dicts with 'id'
        posts_list = []
        for key, val in posts_data.items():
            if isinstance(val, dict):
                val["id"] = key
                # Ensure timestamp is present
                if "timestamp" not in val and "recordCreationDate" in val:
                    val["timestamp"] = val["recordCreationDate"]
                posts_list.append(val)

        # Sort by key descending (newest first) because Firebase returns ascending
        posts_list.sort(key=lambda x: x["id"], reverse=True)

        # Handle cursor and limit
        next_cursor = None

        # If we have a cursor (end_at), the first item in the result (after sorting reverse)
        # might be the cursor itself (because end_at is inclusive).
        if end_at and posts_list and posts_list[0]["id"] == end_at:
            posts_list.pop(0)

        # Now determine next_cursor
        if len(posts_list) > limit:
            # We have more than requested, so we definitely have a next page
            next_cursor = posts_list[limit - 1]["id"]
            posts_list = posts_list[:limit]
        elif len(posts_list) == limit and has_more_possible:
            # We have exactly the limit, and we fetched a full batch.
            # This implies there might be more items preceding these.
            next_cursor = posts_list[-1]["id"]
        else:
            # We have fewer than limit, OR we have limit but didn't fetch a full batch.
            # This means we exhausted the database.
            next_cursor = None

        return posts_list, next_cursor

    except Exception as e:
        current_app.logger.error(f"Error fetching paginated posts: {str(e)}")
        raise


def get_post_by_id(post_id: str) -> Optional[Dict]:
    """
    Fetch a single post by ID.

    Args:
        post_id: The unique post identifier

    Returns:
        Post dictionary with 'id' added, or None if not found
    """
    try:
        ref = get_db_ref(f"posts/{post_id}")
        post_data = ref.get()  # type: ignore[misc]

        if post_data and isinstance(post_data, dict):
            post_data["id"] = post_id  # type: ignore[index]
            return post_data  # type: ignore[return-value]
        return None

    except Exception as e:
        current_app.logger.error(f"Error fetching post {post_id}: {str(e)}")
        raise


def create_post(post_data: Dict) -> str:
    """
    Create a new post in Firebase.

    Args:
        post_data: Dictionary containing post fields (title, content, author_id, etc.)

    Returns:
        The ID of the newly created post
    """
    try:
        ref = get_db_ref("posts")

        # Add timestamp if not present
        if "timestamp" not in post_data:
            post_data["timestamp"] = time.time()

        # Push creates a unique ID
        new_post_ref = ref.push(post_data)  # type: ignore[arg-type]

        post_key = new_post_ref.key if new_post_ref.key else ""
        current_app.logger.info(f"Created post: {post_key}")
        return post_key  # type: ignore[return-value]

    except Exception as e:
        current_app.logger.error(f"Error creating post: {str(e)}")
        raise


def update_post(post_id: str, updates: Dict) -> bool:
    """
    Update an existing post.

    Args:
        post_id: The post ID to update
        updates: Dictionary of fields to update

    Returns:
        True if successful
    """
    try:
        ref = get_db_ref(f"posts/{post_id}")

        # Add updated timestamp
        updates["updated_at"] = time.time()

        ref.update(updates)
        current_app.logger.info(f"Updated post: {post_id}")

        # If score fields are present, also fan-out to artwall mediums for hydration
        score_fields = {
            k: updates.get(k) for k in ("evaluationNum", "ratingNum") if k in updates
        }
        if score_fields:
            try:
                medium_types = ["audio", "drawing", "sculpture", "writing"]
                for medium in medium_types:
                    art_ref = get_db_ref(f"artwall/{medium}/{post_id}")
                    existing = art_ref.get()  # type: ignore[misc]
                    if existing and isinstance(existing, dict):
                        art_ref.update(score_fields)
                        current_app.logger.debug(
                            f"Fan-out scores to artwall/{medium}/{post_id}: {score_fields}"
                        )
            except Exception as fan_err:
                # Non-fatal: log debug so primary write still succeeds
                current_app.logger.debug(
                    f"Score fan-out skipped for {post_id}: {fan_err}"  # type: ignore[name-defined]
                )
        return True

    except Exception as e:
        current_app.logger.error(f"Error updating post {post_id}: {str(e)}")
        raise


def delete_post(post_id: str) -> bool:
    """
    Delete a post from Firebase.

    Args:
        post_id: The post ID to delete

    Returns:
        True if successful
    """
    try:
        ref = get_db_ref(f"posts/{post_id}")
        ref.delete()

        current_app.logger.info(f"Deleted post: {post_id}")
        return True

    except Exception as e:
        current_app.logger.error(f"Error deleting post {post_id}: {str(e)}")
        raise


def create_user_index(user_id: str, post_id: str) -> bool:
    """
    Create a user-post index entry for efficient user-specific queries.
    This implements the "fan-out on write" pattern.

    Args:
        user_id: The user ID
        post_id: The post ID

    Returns:
        True if successful
    """
    try:
        ref = get_db_ref(f"user-posts/{user_id}/{post_id}")
        ref.set(True)
        return True

    except Exception as e:
        current_app.logger.error(f"Error creating user index: {str(e)}")
        raise
