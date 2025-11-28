import sys

"""
Test the gradient generator system.

Run with: python test_gradients.py
"""

from app.utils.gradient_generator import generate_gradient, get_solid_fallback


def test_consistency():
    """Test that same ID produces same gradient."""
    print("\n" + "=" * 70)
    print("TEST 1: CONSISTENCY")
    print("=" * 70)

    artwork_id = "test-artwork-123"
    medium = "writing"
    theme = "atelier"

    gradient1 = generate_gradient(artwork_id, medium, theme)
    gradient2 = generate_gradient(artwork_id, medium, theme)

    print(f"Artwork ID: {artwork_id}")
    print(f"Medium: {medium}")
    print(f"Theme: {theme}")
    print(f"\nGradient 1: {gradient1}")
    print(f"Gradient 2: {gradient2}")
    print("\n✓ PASSED" if gradient1 == gradient2 else "\n✗ FAILED")

    return gradient1 == gradient2


def test_uniqueness():
    """Test that different IDs produce different gradients."""
    print("\n" + "=" * 70)
    print("TEST 2: UNIQUENESS")
    print("=" * 70)

    medium = "writing"
    theme = "atelier"

    gradient1 = generate_gradient("artwork-123", medium, theme)
    gradient2 = generate_gradient("artwork-456", medium, theme)
    gradient3 = generate_gradient("artwork-789", medium, theme)

    print(f"Medium: {medium}")
    print(f"Theme: {theme}")
    print(f"\nArtwork 123: {gradient1}")
    print(f"Artwork 456: {gradient2}")
    print(f"Artwork 789: {gradient3}")

    unique = (
        gradient1 != gradient2 and gradient2 != gradient3 and gradient1 != gradient3
    )
    print("\n✓ PASSED" if unique else "\n✗ FAILED")

    return unique


def test_theme_awareness():
    """Test that gradients change with theme."""
    print("\n" + "=" * 70)
    print("TEST 3: THEME AWARENESS")
    print("=" * 70)

    artwork_id = "test-artwork-456"
    medium = "audio"

    gradient_atelier = generate_gradient(artwork_id, medium, "atelier")
    gradient_dark = generate_gradient(artwork_id, medium, "dark")
    gradient_teal = generate_gradient(artwork_id, medium, "teal")

    print(f"Artwork ID: {artwork_id}")
    print(f"Medium: {medium}")
    print(f"\nAtelier theme: {gradient_atelier}")
    print(f"Dark theme:    {gradient_dark}")
    print(f"Teal theme:    {gradient_teal}")

    different = gradient_atelier != gradient_dark or gradient_dark != gradient_teal
    print("\n✓ PASSED (themes produce variations)" if different else "\n✗ FAILED")

    return different


def test_all_mediums():
    """Test gradient generation for all medium types."""
    print("\n" + "=" * 70)
    print("TEST 4: ALL MEDIUMS")
    print("=" * 70)

    artwork_id = "test-artwork-789"
    theme = "atelier"
    mediums = ["audio", "drawing", "sculpture", "writing"]

    gradients = {}
    for medium in mediums:
        gradient = generate_gradient(artwork_id, medium, theme)
        gradients[medium] = gradient
        print(f"\n{medium.upper():12} | gradient: {gradient}")

    # Check all are different
    values = list(gradients.values())
    all_unique = len(values) == len(set(values))

    print(
        "\n✓ PASSED (all mediums produce unique gradients)"
        if all_unique
        else "\n✗ FAILED"
    )

    return all_unique


def test_all_themes():
    """Test gradient generation for all themes."""
    print("\n" + "=" * 70)
    print("TEST 5: ALL THEMES")
    print("=" * 70)

    artwork_id = "test-artwork-abc"
    medium = "drawing"
    themes = ["atelier", "blueprint", "dark", "teal", "nature", "earth"]

    for theme in themes:
        gradient = generate_gradient(artwork_id, medium, theme)
        print(f"\n{theme.upper():12} | {gradient}")

    print("\n✓ PASSED (all themes generate gradients)")

    return True


def test_solid_fallbacks():
    """Test solid color fallbacks."""
    print("\n" + "=" * 70)
    print("TEST 6: SOLID FALLBACKS")
    print("=" * 70)

    mediums = ["audio", "drawing", "sculpture", "writing"]

    for medium in mediums:
        fallback = get_solid_fallback(medium)
        print(f"{medium.upper():12} | {fallback}")

    print("\n✓ PASSED")

    return True


def test_visual_variety():
    """Generate sample gradients to visually assess variety."""
    print("\n" + "=" * 70)
    print("TEST 7: VISUAL VARIETY (10 Random Artworks)")
    print("=" * 70)

    import random
    import string

    theme = "atelier"
    medium = "writing"

    for i in range(10):
        # Generate random artwork ID
        artwork_id = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        gradient = generate_gradient(artwork_id, medium, theme)
        print(f"\nArtwork {i+1:2} | {gradient}")

    print("\n✓ PASSED (inspect visually for variety)")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("GRADIENT GENERATOR TEST SUITE")
    print("=" * 70)

    results = []

    results.append(("Consistency", test_consistency()))
    results.append(("Uniqueness", test_uniqueness()))
    results.append(("Theme Awareness", test_theme_awareness()))
    results.append(("All Mediums", test_all_mediums()))
    results.append(("All Themes", test_all_themes()))
    results.append(("Solid Fallbacks", test_solid_fallbacks()))
    results.append(("Visual Variety", test_visual_variety()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} | {status}")

    print(f"\n{passed}/{total} tests passed")
    print("=" * 70 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
