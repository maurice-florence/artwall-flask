"""
Custom Jinja2 template filters for Artwall application.
"""

from app.utils.gradient_generator import generate_gradient, get_solid_fallback


def gradient_filter(artwork_id: str, medium: str, theme: str = "atelier") -> str:
    """
    Generate a unique gradient for an artwork card.

    Usage in templates:
        {{ post.id | gradient(post.medium, current_theme) }}
    """
    return generate_gradient(artwork_id, medium, theme)


def solid_fallback_filter(medium: str) -> str:
    """
    Get solid color fallback for a medium.

    Usage in templates:
        {{ post.medium | solid_fallback }}
    """
    return get_solid_fallback(medium)


def register_filters(app):
    """Register all custom filters with the Flask app."""
    app.jinja_env.filters["gradient"] = gradient_filter
    app.jinja_env.filters["solid_fallback"] = solid_fallback_filter
