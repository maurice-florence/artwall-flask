from app.utils.post_helpers import group_posts_by_year


def test_group_posts_by_year_basic():
    posts = [
        {"year": 2025, "id": 1},
        {"year": 2025, "id": 2},
        {"year": 2024, "id": 3},
        {"year": 2023, "id": 4},
        {"year": 2023, "id": 5},
    ]
    grouped = group_posts_by_year(posts)
    assert grouped == [
        (2025, [{"year": 2025, "id": 1}, {"year": 2025, "id": 2}]),
        (2024, [{"year": 2024, "id": 3}]),
        (2023, [{"year": 2023, "id": 4}, {"year": 2023, "id": 5}]),
    ]


def test_group_posts_by_year_empty():
    assert group_posts_by_year([]) == []


def test_group_posts_by_year_unknown():
    posts = [
        {"id": 1},
        {"year": 2025, "id": 2},
        {"id": 3},
    ]
    grouped = group_posts_by_year(posts)
    assert grouped[0][0] == "Unknown"
    assert grouped[1][0] == 2025
    assert grouped[2][0] == "Unknown"
