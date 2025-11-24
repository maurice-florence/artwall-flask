"""
Test the year grouping functionality.

Run with: python test_year_grouping.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.post_helpers import group_posts_by_year
from datetime import datetime


def test_year_grouping():
    """Test that posts are correctly grouped by year."""
    
    # Create test posts with year/month/day fields (like actual data)
    posts = [
        {
            'id': 'post1',
            'title': 'Post from 2024',
            'year': 2024,
            'month': 11,
            'day': 15,
            'medium': 'writing'
        },
        {
            'id': 'post2',
            'title': 'Another 2024 post',
            'year': 2024,
            'month': 3,
            'day': 10,
            'medium': 'drawing'
        },
        {
            'id': 'post3',
            'title': 'Post from 2023',
            'year': 2023,
            'month': 8,
            'day': 20,
            'medium': 'audio'
        },
        {
            'id': 'post4',
            'title': 'Another 2023 post',
            'year': 2023,
            'month': 2,
            'day': 5,
            'medium': 'writing'
        },
        {
            'id': 'post5',
            'title': 'Post from 2022',
            'year': 2022,
            'month': 12,
            'day': 31,
            'medium': 'sculpture'
        },
    ]
    
    grouped = group_posts_by_year(posts)
    
    print("Year Grouping Test")
    print("=" * 60)
    print(f"Total posts: {len(posts)}")
    print(f"Years found: {len(grouped)}")
    print()
    
    for year, year_posts in grouped:
        print(f"\n{year}")
        print("-" * 60)
        for post in year_posts:
            print(f"  - {post['title']} ({post['year']}-{post.get('month', 1):02d}-{post.get('day', 1):02d}) [{post['medium']}]")
    
    # Verify structure
    assert len(grouped) == 3, f"Expected 3 years, got {len(grouped)}"
    assert grouped[0][0] == 2024, f"Expected first year to be 2024, got {grouped[0][0]}"
    assert len(grouped[0][1]) == 2, f"Expected 2 posts in 2024, got {len(grouped[0][1])}"
    assert grouped[1][0] == 2023, f"Expected second year to be 2023, got {grouped[1][0]}"
    assert len(grouped[1][1]) == 2, f"Expected 2 posts in 2023, got {len(grouped[1][1])}"
    assert grouped[2][0] == 2022, f"Expected third year to be 2022, got {grouped[2][0]}"
    assert len(grouped[2][1]) == 1, f"Expected 1 post in 2022, got {len(grouped[2][1])}"
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)


def test_with_year_field():
    """Test grouping when posts have a 'year' field directly."""
    
    posts = [
        {'id': 'p1', 'title': 'Post 1', 'year': 2024, 'medium': 'writing'},
        {'id': 'p2', 'title': 'Post 2', 'year': 2024, 'medium': 'drawing'},
        {'id': 'p3', 'title': 'Post 3', 'year': 2023, 'medium': 'audio'},
    ]
    
    grouped = group_posts_by_year(posts)
    
    print("\n\nYear Field Test")
    print("=" * 60)
    
    for year, year_posts in grouped:
        print(f"\n{year}: {len(year_posts)} post(s)")
        for post in year_posts:
            print(f"  - {post['title']}")
    
    assert len(grouped) == 2, f"Expected 2 years, got {len(grouped)}"
    assert grouped[0][0] == 2024
    assert len(grouped[0][1]) == 2
    
    print("\n✓ Year field test passed!")


def test_empty_posts():
    """Test with empty posts list."""
    
    grouped = group_posts_by_year([])
    assert grouped == [], "Expected empty list for empty input"
    print("\n✓ Empty posts test passed!")


if __name__ == '__main__':
    test_year_grouping()
    test_with_year_field()
    test_empty_posts()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
