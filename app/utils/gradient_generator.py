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
    """Generate a unique, varied linear-gradient.

    Variation dimensions (all hash-driven for consistency per artwork_id):
    - Angle (135–179deg)
    - Stop count (3–5)
    - Non-uniform stop positions
    - Progressive hue shifts + saturation boosts per medium
    - Lightness ramp for depth

    Tests expect the string to begin with 'linear-gradient(' so we keep that.
    """
    theme_colors = THEME_COLORS.get(theme, THEME_COLORS["atelier"])
    base_color = theme_colors.get(medium, theme_colors["drawing"])

    r, g, b = hex_to_rgb(base_color)
    base_h, base_s, base_l = rgb_to_hsl(r, g, b)

    hv = hash_string_to_number(artwork_id)
    hue_variation = HUE_VARIATIONS.get(medium, 25)
    saturation_boost = SATURATION_BOOSTS.get(medium, 18)

    # Dynamic stop count 3–5
    stop_count = 3 + (hv % 3)  # 3,4,5

    # Angle diversity
    angle = (hv % 45) + 135

    # Generate hues incrementally
    colors = []
    current_hue = (base_h + (hv % hue_variation)) % 360
    for i in range(stop_count):
        # Hue shift per stop (mild for coherence)
        shift = 18 + (hv % 12)
        h = (current_hue + shift * i) % 360
        # Saturation variation
        sat = min(96, base_s + saturation_boost + i * 3)
        # Lightness ramp (slightly brighter each step)
        light = max(30, min(65, base_l + i * 5 - 5))
        colors.append((h, sat, light))

    # Derive stop positions (sorted, unique, ending at 100%)
    # Use hash slices to produce fractional positions.
    positions = []
    for i in range(stop_count - 1):
        raw = (hv >> (i * 8)) & 0xFF  # take successive bytes
        pct = 15 + (raw % 70)  # between 15 and 84
        positions.append(pct)
    positions = sorted(set(positions))
    # Ensure we have exactly stop_count-1 interior positions; pad if collisions
    while len(positions) < stop_count - 1:
        positions.append(15 + (len(positions) * 10))
    positions = positions[: stop_count - 1]
    positions.append(100)

    # Normalize first position to 0
    if positions[0] < 5:
        positions[0] = 0
    else:
        positions.insert(0, 0)
        colors.insert(0, colors[0])  # duplicate first color to align
        stop_count += 1

    # Re-trim if overshoot
    if len(colors) < len(positions):
        # Extend last color to match positions length
        last = colors[-1]
        while len(colors) < len(positions):
            colors.append(last)
    elif len(colors) > len(positions):
        colors = colors[: len(positions)]

    # Assemble gradient string
    stops = []
    for (h, s, l), pos in zip(colors, positions):
        stops.append(f"hsl({h}, {s}%, {l}%) {pos}%")

    return f"linear-gradient({angle}deg, {', '.join(stops)})"


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
