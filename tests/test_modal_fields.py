import pytest
from app import create_app
from unittest.mock import patch


# Patch get_paginated_posts before app creation
@pytest.fixture(autouse=True)
def mock_get_paginated_posts(monkeypatch):
    def fake_get_paginated_posts(limit=100, end_at=None):
        return (
            [
                {
                    "id": "1",
                    "title": "Test Post",
                    "content": "This is a test post.",
                    "medium": "writing",
                    "subcategory": "Poetry",
                    "location": "Testville",
                    "location1": "Testville",
                    "location2": "",
                    "year": 2025,
                    "month": 11,
                    "day": 28,
                    "date_str": "2025-11-28",
                    "tags": ["poetry", "test"],
                    "cleaned_content": "This is a test post.",
                },
                {
                    "id": "2",
                    "title": "Another Post",
                    "content": "Another test post.",
                    "medium": "drawing",
                    "subcategory": "Sketch",
                    "location": "Drawtown",
                    "location1": "Drawtown",
                    "location2": "",
                    "year": 2024,
                    "month": 10,
                    "day": 15,
                    "date_str": "2024-10-15",
                    "tags": ["sketch", "art"],
                    "cleaned_content": "Another test post.",
                },
            ],
            None,
        )

    monkeypatch.setattr(
        "app.blueprints.main.routes.get_paginated_posts", fake_get_paginated_posts
    )


@pytest.fixture
def client():
    app = create_app("development")
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_random_modals_have_expected_fields(client):
    # Debug: print all registered endpoints
    print("Registered endpoints:")
    for rule in client.application.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule}")

    # Patch after client/app is created to avoid interfering with blueprint registration
    with patch("app.services.firebase_service.get_paginated_posts") as mock_get_posts:
        mock_get_posts.return_value = (
            [
                {
                    "id": "1",
                    "title": "Test Post",
                    "content": "This is a test post.",
                    "medium": "writing",
                    "subcategory": "Poetry",
                    "location": "Testville",
                    "location1": "Testville",
                    "location2": "",
                    "year": 2025,
                    "month": 11,
                    "day": 28,
                    "date_str": "2025-11-28",
                    "tags": ["poetry", "test"],
                    "cleaned_content": "This is a test post.",
                },
                {
                    "id": "2",
                    "title": "Another Post",
                    "content": "Another test post.",
                    "medium": "drawing",
                    "subcategory": "Sketch",
                    "location": "Drawtown",
                    "location1": "Drawtown",
                    "location2": "",
                    "year": 2024,
                    "month": 10,
                    "day": 15,
                    "date_str": "2024-10-15",
                    "tags": ["sketch", "art"],
                    "cleaned_content": "Another test post.",
                },
            ],
            None,
        )

        response = client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".card")
        if len(cards) == 0:
            print("\nRendered HTML:\n", html)
        assert len(cards) > 0, "No cards found on main page."

        for card in cards[:5]:
            title = card.select_one(".card-title")
            assert title is not None and title.text.strip(), "Title missing in card."
            assert card.has_attr("data-content"), "data-content missing."
            assert card.has_attr("data-date"), "data-date missing."
            assert card.has_attr("data-location"), "data-location missing."
            assert card.has_attr("data-medium"), "data-medium missing."
            assert card.has_attr("data-subcategory"), "data-subcategory missing."
            assert any(
                [
                    card["data-content"],
                    card["data-date"],
                    card["data-location"],
                    card["data-medium"],
                    card["data-subcategory"],
                ]
            ), "All modal fields are empty."
