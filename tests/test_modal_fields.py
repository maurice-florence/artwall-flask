import pytest
from flask import url_for
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_random_modals_have_expected_fields(client):
    # Load the main page and parse a few cards
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Find card blocks (simple string search for demo)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.select('.card')
    assert len(cards) > 0, 'No cards found on main page.'

    # Check a sample of up to 5 cards
    for card in cards[:5]:
        # Title is in the card-title element
        title = card.select_one('.card-title')
        assert title is not None and title.text.strip(), 'Title missing in card.'
        # Data attributes
        assert card.has_attr('data-content'), 'data-content missing.'
        # Modal fields: date, location, medium, subcategory
        assert card.has_attr('data-date'), 'data-date missing.'
        assert card.has_attr('data-location'), 'data-location missing.'
        assert card.has_attr('data-medium'), 'data-medium missing.'
        assert card.has_attr('data-subcategory'), 'data-subcategory missing.'
        # At least one of content, date, location, medium, subcategory should be non-empty
        assert any([
            card['data-content'],
            card['data-date'],
            card['data-location'],
            card['data-medium'],
            card['data-subcategory']
        ]), 'All modal fields are empty.'
