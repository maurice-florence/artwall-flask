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
    limit: int = 20, end_at: Optional[float] = None
) -> Tuple[List[Dict], Optional[float]]:
    """
    Fetch paginated posts using cursor-based pagination.
    Reads from /artwall with subpaths: audio, drawing, sculpture, writing

    Args:
        limit: Number of posts to fetch
        end_at: Cursor (timestamp) to start fetching from (for pagination)

    Returns:
        Tuple of (posts_list, next_cursor)
        - posts_list: List of post dictionaries with 'id' added
        - next_cursor: Timestamp of the last post (for next page), or None if no more
    """
    try:
        # Fetch from all medium types under /artwall
        all_posts = []
        medium_types = ["audio", "drawing", "sculpture", "writing"]

        for medium in medium_types:
            ref = get_db_ref(f"artwall/{medium}")
            result = ref.get()  # type: ignore[misc]

            if result and isinstance(result, dict):
                for post_id, post_data in result.items():
                    if isinstance(post_data, dict):
                        post_data["id"] = post_id
                        post_data["medium"] = medium  # Add medium type for display
                        # Use recordCreationDate as timestamp if timestamp doesn't exist
                        if (
                            "timestamp" not in post_data
                            and "recordCreationDate" in post_data
                        ):
                            post_data["timestamp"] = post_data["recordCreationDate"]
                        all_posts.append(post_data)

        if not all_posts:
            return [], None

        # Sort by actual artwork creation date (year, month, day) descending (newest first)
        # Create a sortable date value from year/month/day fields
        def get_sort_key(post):
            year = post.get("year", 0) or 0
            month = post.get("month", 1) or 1
            day = post.get("day", 1) or 1
            # Create sortable integer: YYYYMMDD
            return year * 10000 + month * 100 + day

        all_posts.sort(key=get_sort_key, reverse=True)

        # Apply cursor filtering if provided (cursor is now an index/offset)
        start_index = 0
        if end_at is not None:
            start_index = int(end_at)

        # Take posts from start_index to start_index + limit
        posts = all_posts[start_index : start_index + limit]  # noqa: E203

        # Determine next cursor
        next_cursor = None
        if len(all_posts) > start_index + limit:
            # More posts available - next cursor is the next starting index
            next_cursor = start_index + limit

        return posts, next_cursor

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
