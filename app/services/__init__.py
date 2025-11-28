"""
Services Package.
Contains business logic for Firebase operations and data processing.
"""

from app.services.firebase_service import (
    init_firebase,
    get_paginated_posts,
    get_post_by_id,
    create_post,
    update_post,
    delete_post,
)
from app.services.project_service import ProjectService

__all__ = [
    "init_firebase",
    "get_paginated_posts",
    "get_post_by_id",
    "create_post",
    "update_post",
    "delete_post",
    "ProjectService",
]
