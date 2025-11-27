"""
Test Database Loading
Compare what's in Firebase vs what the app loads
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from app.services.firebase_service import get_paginated_posts
from collections import defaultdict

load_dotenv()

def init_firebase():
    """Initialize Firebase"""
    if not firebase_admin._apps:
        cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        db_url = os.environ.get('FIREBASE_DATABASE_URL')
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': db_url
        })

def test_database_structure():
    """Test 1: Check database structure"""
    print("\n" + "="*70)
    print("TEST 1: DATABASE STRUCTURE")
    print("="*70)
    
    ref = db.reference('/artwall')
    data = ref.get()  # type: ignore[misc]
    assert isinstance(data, dict)
    
    if not data:
        print("❌ No data found at /artwall")
        return False
    
    print(f"✓ Found medium types: {list(data.keys())}")
    
    total_items = 0
    medium_counts = {}
    
    for medium in data.keys():
        if isinstance(data[medium], dict):
            count = len(data[medium])
            medium_counts[medium] = count
            total_items += count
            print(f"  - {medium}: {count} items")
    
    print(f"\n✓ Total items in database: {total_items}")
    return medium_counts

def test_app_loading():
    """Test 2: Check what the app loads"""
    print("\n" + "="*70)
    print("TEST 2: APP LOADING")
    print("="*70)
    
    try:
        # Create Flask app context
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Load all posts (high limit to get everything)
            posts, next_cursor = get_paginated_posts(limit=1000)
            
            print(f"✓ App loaded {len(posts)} posts")
            
            # Count by medium
            app_counts = defaultdict(int)
            for post in posts:
                medium = post.get('medium', 'unknown')
                app_counts[medium] += 1
            
            print("\nMedium distribution in app:")
            for medium, count in sorted(app_counts.items()):
                print(f"  - {medium}: {count} items")
            
            return dict(app_counts), posts
    except Exception as e:
        print(f"❌ Error loading posts: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}, []

def test_sample_posts():
    """Test 3: Sample posts from each medium"""
    print("\n" + "="*70)
    print("TEST 3: SAMPLE POSTS FROM EACH MEDIUM")
    print("="*70)
    
    medium_types = ['audio', 'drawing', 'sculpture', 'writing']
    samples = {}
    
    for medium in medium_types:
        ref = db.reference(f'/artwall/{medium}')
        data = ref.get()  # type: ignore[misc]
        
        if data and isinstance(data, dict):
            # Get first 3 items
            items = list(data.items())[:3]
            samples[medium] = items
            
            print(f"\n{medium.upper()} samples:")
            for post_id, post_data in items:
                title = post_data.get('title', 'No title')
                timestamp = post_data.get('timestamp')
                record_date = post_data.get('recordCreationDate')
                year = post_data.get('year')
                
                print(f"  - ID: {post_id}")
                print(f"    Title: {title[:50]}")
                print(f"    Year: {year}")
                print(f"    Timestamp: {timestamp}")
                print(f"    RecordCreationDate: {record_date}")
                print()
    
    return samples

def test_timestamp_sorting():
    """Test 4: Check if timestamps exist and are valid"""
    print("\n" + "="*70)
    print("TEST 4: TIMESTAMP ANALYSIS")
    print("="*70)
    
    medium_types = ['audio', 'drawing', 'sculpture', 'writing']
    
    for medium in medium_types:
        ref = db.reference(f'/artwall/{medium}')
        data = ref.get()  # type: ignore[misc]
        
        if data and isinstance(data, dict):
            has_timestamp = 0
            has_record_date = 0
            has_both = 0
            has_neither = 0
            
            for post_id, post_data in data.items():
                ts = post_data.get('timestamp')
                rd = post_data.get('recordCreationDate')
                
                if ts and rd:
                    has_both += 1
                elif ts:
                    has_timestamp += 1
                elif rd:
                    has_record_date += 1
                else:
                    has_neither += 1
            
            total = len(data)
            print(f"\n{medium.upper()} ({total} items):")
            print(f"  - Has both timestamp & recordCreationDate: {has_both}")
            print(f"  - Has only timestamp: {has_timestamp}")
            print(f"  - Has only recordCreationDate: {has_record_date}")
            print(f"  - Has neither: {has_neither}")

def compare_results(db_counts, app_counts):
    """Test 5: Compare database vs app"""
    print("\n" + "="*70)
    print("TEST 5: COMPARISON")
    print("="*70)
    
    all_mediums = set(list(db_counts.keys()) + list(app_counts.keys()))
    
    print(f"\n{'Medium':<15} {'Database':<12} {'App':<12} {'Match':<8}")
    print("-" * 50)
    
    all_match = True
    for medium in sorted(all_mediums):
        db_count = db_counts.get(medium, 0)
        app_count = app_counts.get(medium, 0)
        match = "✓" if db_count == app_count else "✗"
        
        if db_count != app_count:
            all_match = False
        
        print(f"{medium:<15} {db_count:<12} {app_count:<12} {match:<8}")
    
    print()
    if all_match:
        print("✓ All mediums match!")
    else:
        print("✗ Mismatch detected!")
    
    return all_match

def test_specific_medium_audio():
    """Test 6: Deep dive into audio medium"""
    medium = 'audio'
    print("\n" + "="*70)
    print(f"TEST 6: DEEP DIVE - {medium.upper()}")
    print("="*70)
    ref = db.reference(f'/artwall/{medium}')
    db_data = ref.get()  # type: ignore[misc]
    assert isinstance(db_data, dict)
    if not db_data:
        print(f"❌ No data in database for {medium}")
        return
    db_ids = set(db_data.keys())
    print(f"Database has {len(db_ids)} {medium} items")
    from app import create_app
    app = create_app()
    with app.app_context():
        posts, _ = get_paginated_posts(limit=1000)
        app_posts = [p for p in posts if p.get('medium') == medium]
        app_ids = set(p.get('id') for p in app_posts)
        print(f"App loaded {len(app_ids)} {medium} items")
        missing = db_ids - app_ids
        if missing:
            print(f"\n❌ Missing {len(missing)} items from app:")
            for post_id in list(missing)[:5]:
                post_data = db_data[post_id]
                print(f"  - {post_id}: {post_data.get('title', 'No title')[:50]}")
                print(f"    timestamp: {post_data.get('timestamp')}")
                print(f"    recordCreationDate: {post_data.get('recordCreationDate')}")
        else:
            print(f"✓ All {medium} items loaded correctly")

def main():
    """Run all tests"""
    print("\n" + "🔥"*35)
    print("  ARTWALL DATABASE TEST SUITE")
    print("🔥"*35)
    
    init_firebase()
    
    # Test 1: Database structure
    db_counts = test_database_structure()
    
    # Test 2: App loading
    app_counts, posts = test_app_loading()
    
    # Test 3: Sample posts
    test_sample_posts()
    
    # Test 4: Timestamp analysis
    test_timestamp_sorting()
    
    # Test 5: Comparison
    if db_counts and app_counts:
        match = compare_results(db_counts, app_counts)
        
        # Test 6: Deep dive if mismatch
        if not match:
            print("\n" + "="*70)
            print("INVESTIGATING MISMATCHES...")
            print("="*70)
            
            for medium in ['audio', 'drawing', 'sculpture', 'writing']:
                if db_counts.get(medium, 0) != app_counts.get(medium, 0):
                    test_specific_medium(medium, posts)
    
    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)

if __name__ == '__main__':
    main()
