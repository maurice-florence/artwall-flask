"""
Helper functions for post processing.
"""
from typing import List, Dict, Tuple
from datetime import datetime


def group_posts_by_year(posts: List[Dict]) -> List[Tuple[int, List[Dict]]]:
    """
    Group posts by year, maintaining chronological order (newest first).
    
    Args:
        posts: List of post dictionaries (should already be sorted by date descending)
    
    Returns:
        List of tuples (year, posts_for_that_year)
        Example: [(2024, [post1, post2]), (2023, [post3, post4])]
    """
    if not posts:
        return []
    
    grouped = []
    current_year = None
    current_group = []
    
    for post in posts:
        # Get year from the year field (actual artwork creation year)
        year = post.get('year')
        
        # If we don't have a year, use "Unknown"
        if not year:
            year = 'Unknown'
        
        if year != current_year:
            # Save previous group if it exists
            if current_group:
                grouped.append((current_year, current_group))
            
            # Start new group
            current_year = year
            current_group = [post]
        else:
            current_group.append(post)
    
    # Don't forget the last group
    if current_group and current_year is not None:
        grouped.append((current_year, current_group))
    
    return grouped
