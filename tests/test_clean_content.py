import pytest
from app.utils.clean_content import clean_post_content

def test_clean_post_content_removes_title_and_footer():
    content = """Title of Poem\nThis is the first line.\nThis is the second line.\nOctober 5, 2025\nAmsterdam"""
    cleaned = clean_post_content(content)
    assert cleaned == "This is the first line.\nThis is the second line."

def test_clean_post_content_handles_blank_lines():
    content = """

Title\n\nBody line 1.\nBody line 2.\n\n2025-11-27\nRotterdam\n\n"""
    cleaned = clean_post_content(content)
    assert cleaned == "Body line 1.\nBody line 2."

def test_clean_post_content_short_content():
    content = "Title\nOnly one line"
    cleaned = clean_post_content(content)
    assert cleaned == "Only one line"

def test_clean_post_content_empty():
    assert clean_post_content("") == ""
    assert clean_post_content(None) == ""
