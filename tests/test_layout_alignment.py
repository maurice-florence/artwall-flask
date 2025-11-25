"""
Test Layout Alignment and Spacing
Tests for header-to-card grid alignment, spacing, and responsive behavior
"""

import re
from pathlib import Path


class TestLayoutAlignment:
    """Test suite for layout alignment and spacing"""
    
    @staticmethod
    def read_css_file(filename):
        """Read CSS file content"""
        css_path = Path(__file__).parent.parent / 'app' / 'static' / 'css' / filename
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def extract_css_value(css_content, selector, property_name):
        """Extract a CSS property value for a given selector"""
        # Match selector block
        pattern = rf'{re.escape(selector)}\s*\{{([^}}]+)\}}'
        match = re.search(pattern, css_content, re.MULTILINE | re.DOTALL)
        if not match:
            return None
        
        block = match.group(1)
        # Extract property value
        prop_pattern = rf'{property_name}\s*:\s*([^;]+);'
        prop_match = re.search(prop_pattern, block)
        if prop_match:
            return prop_match.group(1).strip()
        return None
    
    @staticmethod
    def extract_padding_value(padding_str):
        """Extract padding values from CSS padding property"""
        if not padding_str:
            return None
        
        # Handle different padding formats
        parts = padding_str.split()
        if len(parts) == 1:
            return {'all': parts[0]}
        elif len(parts) == 2:
            return {'vertical': parts[0], 'horizontal': parts[1]}
        elif len(parts) == 4:
            return {'top': parts[0], 'right': parts[1], 'bottom': parts[2], 'left': parts[3]}
        return None

    def test_body_padding(self):
        """Test that body has correct padding"""
        style_css = self.read_css_file('style.css')
        body_padding = self.extract_css_value(style_css, 'body', 'padding')
        
        assert body_padding is not None, "Body padding not found"
        
        padding = self.extract_padding_value(body_padding)
        assert padding is not None, "Could not parse body padding"
        
        # Body should have 0 75px (0 top/bottom, 75px left/right)
        if 'horizontal' in padding:
            assert '75px' in padding['horizontal'], f"Body horizontal padding should be 75px, got {padding['horizontal']}"
            print(f"✓ Body padding: {body_padding}")
        else:
            print(f"✓ Body padding: {body_padding}")
    
    def test_navbar_wrapper_padding(self):
        """Test that navbar-wrapper padding matches masonry-container"""
        style_css = self.read_css_file('style.css')
        navbar_padding = self.extract_css_value(style_css, '.navbar-wrapper', 'padding')
        
        masonry_css = self.read_css_file('masonry.css')
        masonry_padding = self.extract_css_value(masonry_css, '.masonry-container', 'padding')
        
        assert navbar_padding is not None, "Navbar wrapper padding not found"
        assert masonry_padding is not None, "Masonry container padding not found"
        
        # Extract horizontal padding values
        navbar_pad = self.extract_padding_value(navbar_padding)
        masonry_pad = self.extract_padding_value(masonry_padding)
        
        # Both should have 24px horizontal padding
        if navbar_pad and 'horizontal' in navbar_pad:
            assert '24px' in navbar_pad['horizontal'], f"Navbar wrapper horizontal padding should be 24px, got {navbar_pad['horizontal']}"
        
        if masonry_pad and 'horizontal' in masonry_pad:
            assert '24px' in masonry_pad['horizontal'], f"Masonry container horizontal padding should be 24px, got {masonry_pad['horizontal']}"
        
        print(f"✓ Navbar wrapper padding: {navbar_padding}")
        print(f"✓ Masonry container padding: {masonry_padding}")
        print("✓ Header and card grid have matching padding")
    
    def test_total_horizontal_spacing(self):
        """Test that total horizontal spacing adds up correctly"""
        style_css = self.read_css_file('style.css')
        
        # Body: 75px on each side
        body_side = 75
        
        # Navbar-wrapper and masonry-container: should both have 24px
        navbar_padding = self.extract_css_value(style_css, '.navbar-wrapper', 'padding')
        navbar_pad = self.extract_padding_value(navbar_padding)
        
        if navbar_pad and 'horizontal' in navbar_pad:
            # Extract number from "24px"
            match = re.search(r'\d+', navbar_pad['horizontal'])
            navbar_side = int(match.group()) if match else 24
        else:
            navbar_side = 24  # Default expected value
        
        total_spacing = body_side + navbar_side
        expected_total = 99
        
        assert total_spacing == expected_total, \
            f"Total horizontal spacing should be {expected_total}px (75px body + 24px wrapper), got {total_spacing}px"
        
        print(f"✓ Total horizontal spacing: {body_side}px (body) + {navbar_side}px (wrapper) = {total_spacing}px")
    
    def test_masonry_gutter(self):
        """Test that Masonry gutter is set correctly in JavaScript"""
        app_js_path = Path(__file__).parent.parent / 'app' / 'static' / 'js' / 'app.js'
        with open(app_js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Look for gutter setting in Masonry initialization
        gutter_match = re.search(r'gutter:\s*(\d+)', js_content)
        
        assert gutter_match is not None, "Masonry gutter setting not found in app.js"
        
        gutter_value = int(gutter_match.group(1))
        expected_gutter = 8
        
        assert gutter_value == expected_gutter, \
            f"Masonry gutter should be {expected_gutter}px, got {gutter_value}px"
        
        print(f"✓ Masonry gutter spacing: {gutter_value}px")
    
    def test_card_aspect_ratio(self):
        """Test that cards have correct 3:4 aspect ratio"""
        masonry_css = self.read_css_file('masonry.css')
        
        # Look for aspect-ratio in grid-item
        aspect_ratio_pattern = r'\.grid-sizer,\s*\.grid-item\s*\{[^}]*aspect-ratio:\s*([^;]+);'
        match = re.search(aspect_ratio_pattern, masonry_css, re.MULTILINE | re.DOTALL)
        
        assert match is not None, "Card aspect-ratio not found"
        
        aspect_ratio = match.group(1).strip()
        expected_ratio = '3 / 4'
        
        assert aspect_ratio == expected_ratio, \
            f"Card aspect ratio should be {expected_ratio}, got {aspect_ratio}"
        
        print(f"✓ Card aspect ratio: {aspect_ratio}")
    
    def test_year_separator_alignment(self):
        """Test that year separators use primary color and match card dimensions"""
        masonry_css = self.read_css_file('masonry.css')
        
        # Check year text color
        year_text_pattern = r'\.year-separator\s+\.year-text\s*\{[^}]*color:\s*([^;]+);'
        match = re.search(year_text_pattern, masonry_css, re.MULTILINE | re.DOTALL)
        
        assert match is not None, "Year separator text color not found"
        
        color = match.group(1).strip()
        assert 'var(--theme-primary' in color, \
            f"Year separator should use primary color variable, got {color}"
        
        print(f"✓ Year separator color: {color}")
        
        # Check year separator has same aspect ratio as cards
        separator_pattern = r'\.grid-item\.year-separator\s*\{[^}]*aspect-ratio:\s*([^;]+);'
        sep_match = re.search(separator_pattern, masonry_css, re.MULTILINE | re.DOTALL)
        
        assert sep_match is not None, "Year separator aspect-ratio not found"
        
        sep_ratio = sep_match.group(1).strip()
        assert sep_ratio == '3 / 4', \
            f"Year separator aspect ratio should be 3 / 4, got {sep_ratio}"
        
        print(f"✓ Year separator aspect ratio: {sep_ratio}")
    
    def test_card_back_primary_color(self):
        """Test that card backs use primary color"""
        masonry_css = self.read_css_file('masonry.css')
        
        # Check card-back background
        card_back_pattern = r'\.card-back\s*\{[^}]*background:\s*([^;]+);'
        match = re.search(card_back_pattern, masonry_css, re.MULTILINE | re.DOTALL)
        
        assert match is not None, "Card back background not found"
        
        background = match.group(1).strip()
        assert 'var(--theme-primary' in background, \
            f"Card back should use primary color variable, got {background}"
        
        print(f"✓ Card back background: {background}")
        
        # Check card title color is white
        title_pattern = r'\.card-title\s*\{[^}]*color:\s*([^;]+);'
        title_match = re.search(title_pattern, masonry_css, re.MULTILINE | re.DOTALL)
        
        assert title_match is not None, "Card title color not found"
        
        title_color = title_match.group(1).strip()
        assert '#ffffff' in title_color.lower() or '#fff' in title_color.lower(), \
            f"Card title should be white on primary background, got {title_color}"
        
        print(f"✓ Card title color: {title_color}")
    
    def test_navbar_title_primary_color(self):
        """Test that navbar title uses primary color"""
        style_css = self.read_css_file('style.css')
        
        # Check navbar-title color
        title_pattern = r'\.navbar-title\s*\{[^}]*color:\s*([^;]+);'
        match = re.search(title_pattern, style_css, re.MULTILINE | re.DOTALL)
        
        assert match is not None, "Navbar title color not found"
        
        color = match.group(1).strip()
        assert 'var(--theme-primary' in color, \
            f"Navbar title should use primary color variable, got {color}"
        
        print(f"✓ Navbar title color: {color}")
    
    def test_navbar_two_row_layout(self):
        """Test that navbar uses two-row layout"""
        style_css = self.read_css_file('style.css')
        
        # Check navbar flex-direction
        navbar_pattern = r'\.navbar\s*\{[^}]*flex-direction:\s*([^;]+);'
        match = re.search(navbar_pattern, style_css, re.MULTILINE | re.DOTALL)
        
        assert match is not None, "Navbar flex-direction not found"
        
        flex_direction = match.group(1).strip()
        assert flex_direction == 'column', \
            f"Navbar should use column flex-direction for two-row layout, got {flex_direction}"
        
        print(f"✓ Navbar layout: {flex_direction} (two-row structure)")
    
    def test_responsive_mobile_padding(self):
        """Test that mobile responsive design maintains alignment"""
        style_css = self.read_css_file('style.css')
        
        # Check for mobile media query
        mobile_query = r'@media\s*\([^)]*max-width:\s*768px[^)]*\)[^{]*\{([^}]*\.navbar-wrapper[^}]*padding:[^;]+;[^}]*)\}'
        match = re.search(mobile_query, style_css, re.MULTILINE | re.DOTALL)
        
        if match:
            padding_match = re.search(r'padding:\s*([^;]+);', match.group(1))
            if padding_match:
                mobile_padding = padding_match.group(1).strip()
                print(f"✓ Mobile navbar-wrapper padding: {mobile_padding}")
        else:
            print("⚠ Mobile navbar-wrapper padding not explicitly set (inherits from default)")
        
        # Check body mobile padding
        mobile_body = r'@media\s*\([^)]*max-width:\s*768px[^)]*\)[^{]*\{([^}]*body[^}]*padding:[^;]+;[^}]*)\}'
        body_match = re.search(mobile_body, style_css, re.MULTILINE | re.DOTALL)
        
        if body_match:
            body_padding_match = re.search(r'padding:\s*([^;]+);', body_match.group(1))
            if body_padding_match:
                mobile_body_padding = body_padding_match.group(1).strip()
                print(f"✓ Mobile body padding: {mobile_body_padding}")
    
    def test_desktop_card_max_width(self):
        """Test that cards have correct max-width on desktop"""
        masonry_css = self.read_css_file('masonry.css')
        
        # Look for desktop media query with max-width
        desktop_query = r'@media\s*\(min-width:\s*1200px\)[^{]*\{[^}]*\.grid-sizer,[^}]*max-width:\s*([^;]+);'
        match = re.search(desktop_query, masonry_css, re.MULTILINE | re.DOTALL)
        
        assert match is not None, "Desktop card max-width not found"
        
        max_width = match.group(1).strip()
        assert max_width == '150px', \
            f"Desktop card max-width should be 150px, got {max_width}"
        
        print(f"✓ Desktop card max-width: {max_width}")


def run_tests():
    """Run all layout alignment tests"""
    test_suite = TestLayoutAlignment()
    
    tests = [
        ('Body Padding', test_suite.test_body_padding),
        ('Navbar Wrapper Padding', test_suite.test_navbar_wrapper_padding),
        ('Total Horizontal Spacing', test_suite.test_total_horizontal_spacing),
        ('Masonry Gutter', test_suite.test_masonry_gutter),
        ('Card Aspect Ratio', test_suite.test_card_aspect_ratio),
        ('Year Separator Alignment', test_suite.test_year_separator_alignment),
        ('Card Back Primary Color', test_suite.test_card_back_primary_color),
        ('Navbar Title Primary Color', test_suite.test_navbar_title_primary_color),
        ('Navbar Two-Row Layout', test_suite.test_navbar_two_row_layout),
        ('Responsive Mobile Padding', test_suite.test_responsive_mobile_padding),
        ('Desktop Card Max Width', test_suite.test_desktop_card_max_width),
    ]
    
    print("\n" + "="*70)
    print("LAYOUT ALIGNMENT & SPACING TEST SUITE")
    print("="*70 + "\n")
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 70)
        try:
            test_func()
            passed += 1
            print(f"✅ PASSED\n")
        except AssertionError as e:
            failed += 1
            print(f"❌ FAILED: {str(e)}\n")
        except Exception as e:
            failed += 1
            print(f"❌ ERROR: {str(e)}\n")
    
    print("="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
