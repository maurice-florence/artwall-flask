"""
Gradient Generator for Artwall Cards

Generates unique, theme-aware gradients for artwork cards based on:
- Artwork ID (ensures consistency)
- Medium type (different color ranges per category)
- Active theme (adapts to current color scheme)
"""

import hashlib
from typing import Tuple


# Theme color configurations
THEME_COLORS = {
    "atelier": {
        "audio": "#0b8783",  # Teal
        "drawing": "#7c3aed",  # Purple
        "sculpture": "#ea580c",  # Orange
        "writing": "#2563eb",  # Blue
    },
    "blueprint": {
        "audio": "#1e40af",  # Deep blue
        "drawing": "#7c3aed",  # Purple
        "sculpture": "#ea580c",  # Orange
        "writing": "#2563eb",  # Blue
    },
    "dark": {
        "audio": "#0b8783",  # Teal
        "drawing": "#7c3aed",  # Purple
        "sculpture": "#ea580c",  # Orange
        "writing": "#2563eb",  # Blue
    },
    "teal": {
        "audio": "#0f766e",  # Teal
        "drawing": "#7c3aed",  # Purple
        "sculpture": "#ea580c",  # Orange
        "writing": "#2563eb",  # Blue
    },
    "nature": {
        "audio": "#16a34a",  # Green
        "drawing": "#7c3aed",  # Purple
        "sculpture": "#ea580c",  # Orange
        "writing": "#2563eb",  # Blue
    },
    "earth": {
        "audio": "#92400e",  # Brown
        "drawing": "#7c3aed",  # Purple
        "sculpture": "#ea580c",  # Orange
        "writing": "#2563eb",  # Blue
    },
}

# Hue variation ranges for different mediums
HUE_VARIATIONS = {"writing": 20, "audio": 30, "drawing": 25, "sculpture": 35}

# Saturation boost for visual interest
SATURATION_BOOSTS = {"writing": 15, "audio": 20, "drawing": 18, "sculpture": 22}


def hash_string_to_number(text: str) -> int:
    """Convert string to a consistent numeric hash."""
    return int(hashlib.md5(text.encode()).hexdigest(), 16)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """Convert RGB to HSL (Hue, Saturation, Lightness)."""
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    max_c = max(r_norm, g_norm, b_norm)
    min_c = min(r_norm, g_norm, b_norm)
    lightness_val = (max_c + min_c) / 2.0

    if max_c == min_c:
        h = s = 0.0
    else:
        diff = max_c - min_c
        s = (
            diff / (2.0 - max_c - min_c)
            if lightness_val > 0.5
            else diff / (max_c + min_c)
        )

        if max_c == r_norm:
            h = (g_norm - b_norm) / diff + (6 if g_norm < b_norm else 0)
        elif max_c == g_norm:
            h = (b_norm - r_norm) / diff + 2
        else:
            h = (r_norm - g_norm) / diff + 4
        h /= 6.0

    hue: int = int(h * 360)
    saturation: int = int(s * 100)
    lightness: int = int(lightness_val * 100)
    return (hue, saturation, lightness)


def generate_gradient(artwork_id: str, medium: str, theme: str = "atelier") -> str:
    """
    Generate a unique CSS gradient for an artwork card.

    Args:
        artwork_id: Unique identifier for the artwork (e.g., post ID)
        medium: Type of artwork (audio, drawing, sculpture, writing)
        theme: Active theme name (default: 'atelier')

    Returns:
        CSS linear-gradient string

    Examples:
        >>> generate_gradient('post123', 'writing', 'atelier')
        'linear-gradient(157deg, hsl(210, 85%, 45%) 0%, hsl(240, 90%, 50%) 50%, hsl(270, 85%, 55%) 100%)'
    """
    # Get theme colors
    theme_colors = THEME_COLORS.get(theme, THEME_COLORS["atelier"])
    base_color = theme_colors.get(medium, theme_colors["drawing"])

    # Convert base color to HSL
    r, g, b = hex_to_rgb(base_color)
    theme_h, theme_s, theme_l = rgb_to_hsl(r, g, b)

    # Get hash-based values for consistency
    hash_value = hash_string_to_number(artwork_id)

    # Configuration for this medium
    hue_variation = HUE_VARIATIONS.get(medium, 25)
    saturation_boost = SATURATION_BOOSTS.get(medium, 18)

    # Generate three color stops with variation
    hue1 = (theme_h + (hash_value % hue_variation)) % 360
    hue2 = (hue1 + 25) % 360
    hue3 = (hue2 + 25) % 360

    # Boost saturation for vibrancy
    sat1 = min(95, theme_s + saturation_boost)
    sat2 = min(98, theme_s + saturation_boost + 5)
    sat3 = min(95, theme_s + saturation_boost + 3)

    # Adjust lightness for gradient effect (lighter as it progresses)
    light1 = max(35, min(50, theme_l - 5))
    light2 = max(40, min(55, theme_l))
    light3 = max(45, min(60, theme_l + 5))

    # Calculate gradient angle (135-180 degrees for diagonal)
    angle = (hash_value % 45) + 135

    # Build gradient string
    color1 = f"hsl({hue1}, {sat1}%, {light1}%)"
    color2 = f"hsl({hue2}, {sat2}%, {light2}%)"
    color3 = f"hsl({hue3}, {sat3}%, {light3}%)"

    return f"linear-gradient({angle}deg, {color1} 0%, {color2} 50%, {color3} 100%)"


def generate_gradient_inline(
    artwork_id: str, medium: str, theme: str = "atelier"
) -> str:
    """
    Generate gradient as inline style attribute value.

    Args:
        artwork_id: Unique identifier for the artwork
        medium: Type of artwork (audio, drawing, sculpture, writing)
        theme: Active theme name

    Returns:
        String suitable for style="background: {result}"
    """
    return generate_gradient(artwork_id, medium, theme)


def get_solid_fallback(medium: str) -> str:
    """
    Get a solid color fallback for browsers that don't support gradients.

    Args:
        medium: Type of artwork

    Returns:
        Hex color string
    """
    fallbacks = {
        "audio": "#dc2626",
        "drawing": "#7c3aed",
        "sculpture": "#ea580c",
        "writing": "#2563eb",
    }
    return fallbacks.get(medium, "#7c3aed")


if __name__ == "__main__":
    # Test gradient generation
    print("Testing Gradient Generator\n" + "=" * 50)

    test_artworks = [
        ("artwork-123", "writing"),
        ("artwork-456", "audio"),
        ("artwork-789", "drawing"),
        ("artwork-abc", "sculpture"),
    ]

    for theme_name in ["atelier", "dark", "teal"]:
        print(f"\nTheme: {theme_name.upper()}")
        print("-" * 50)

        for artwork_id, medium in test_artworks:
            gradient = generate_gradient(artwork_id, medium, theme_name)
            print(f"{medium:12} | {gradient}")

    # Test consistency
    print("\n\nConsistency Test")
    print("=" * 50)
    g1 = generate_gradient("test-123", "writing", "atelier")
    g2 = generate_gradient("test-123", "writing", "atelier")
    print(f"Same ID, same result: {g1 == g2}")

    g3 = generate_gradient("test-456", "writing", "atelier")
    print(f"Different ID, different result: {g1 != g3}")
