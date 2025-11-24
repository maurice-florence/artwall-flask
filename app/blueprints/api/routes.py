"""
API Routes.
Handles HTMX requests for dynamic content (load more, etc.).
Returns HTML fragments, not JSON.
"""
from flask import request, render_template, current_app, jsonify
from app.blueprints.api import api_bp
from app.services.firebase_service import get_paginated_posts
from app.utils.post_helpers import group_posts_by_year

@api_bp.route('/load-more')
def load_more():
    """
    HTMX endpoint for loading more posts.
    Returns HTML fragments to be appended to the grid.
    
    Query Parameters:
        cursor: The index/offset of the last post from the previous page
    """
    cursor = request.args.get('cursor')
    
    current_app.logger.info(f"Load more requested with cursor: {cursor}")
    
    if not cursor:
        return "No cursor provided", 400
    
    try:
        # Convert cursor to integer (it's now an index/offset)
        cursor_value = int(cursor)
        
        # Fetch next 100 posts starting after the cursor
        posts, next_cursor = get_paginated_posts(limit=100, end_at=cursor_value)
        
        current_app.logger.info(f"Loaded {len(posts)} posts, next cursor: {next_cursor}")
        
        # Group posts by year
        grouped_posts = group_posts_by_year(posts)
        
        # Return ONLY the grid items partial, not the full page
        return render_template('partials/grid_items.html', 
                             grouped_posts=grouped_posts,
                             next_cursor=next_cursor)
    except ValueError:
        return "Invalid cursor format", 400
    except Exception as e:
        current_app.logger.error(f"Error loading more posts: {str(e)}")
        return f"Error: {str(e)}", 500

@api_bp.route('/search')
def search():
    """
    HTMX endpoint for searching posts.
    Returns filtered HTML fragments.
    """
    query = request.args.get('q', '')
    
    if not query:
        return render_template('partials/grid_items.html', posts=[], next_cursor=None)
    
    try:
        # TODO: Implement search functionality in firebase_service
        # For now, return empty results
        return render_template('partials/grid_items.html', posts=[], next_cursor=None)
    except Exception as e:
        current_app.logger.error(f"Error searching posts: {str(e)}")
        return f"Error: {str(e)}", 500
