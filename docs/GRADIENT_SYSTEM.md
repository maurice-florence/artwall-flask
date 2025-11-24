# Gradient Generator Documentation

## Overview

The Artwall application features a dynamic gradient generation system that creates unique, theme-aware gradients for each artwork card. This system ensures:

1. **Consistency**: Each artwork always displays the same gradient (based on its ID)
2. **Uniqueness**: Different artworks get visually distinct gradients
3. **Theme Awareness**: Gradients adapt to the active color theme
4. **Medium Differentiation**: Different mediums (audio, drawing, sculpture, writing) use different color ranges

## Architecture

The gradient system has two components:

### 1. Python Backend (`app/utils/gradient_generator.py`)

- Generates gradients server-side during template rendering
- Provides initial gradients for faster page load
- Used in Jinja2 templates via custom filters

### 2. JavaScript Frontend (`app/static/js/gradient.js`)

- Regenerates gradients when theme changes
- Handles dynamically loaded content (HTMX pagination)
- Provides instant visual feedback without server round-trips

## Usage

### In Templates

Use the custom Jinja2 filter to generate gradients:

```html
<div class="card-front" 
     data-artwork-id="{{ post.id }}" 
     style="background: {{ post.id | gradient(post.medium) }};">
</div>
```

The filter automatically uses the default 'atelier' theme for initial render.

### Theme-Aware Regeneration

Gradients automatically update when users switch themes via the theme selector. No additional code needed - handled by `gradient.js`.

### Dynamic Content

When new cards load via HTMX (infinite scroll), gradients are automatically generated for them.

## Algorithm

### Hash Generation

Each artwork ID is converted to a consistent numeric hash:

```python
hash = md5(artwork_id.encode()).hexdigest()
numeric_hash = int(hash, 16)
```

### Color Calculation

1. **Base Color**: Select from theme colors based on medium type
2. **Convert to HSL**: Easier to manipulate hue, saturation, lightness
3. **Generate Variations**: Create 3 color stops with slight hue shifts
4. **Boost Saturation**: Add vibrancy (+15-22% depending on medium)
5. **Adjust Lightness**: Create gradient effect (darker → lighter)
6. **Calculate Angle**: Diagonal gradient (135-180°) based on hash

### Example Output

```css
linear-gradient(157deg, 
    hsl(210, 85%, 45%) 0%, 
    hsl(235, 90%, 50%) 50%, 
    hsl(260, 85%, 55%) 100%)
```

## Configuration

### Theme Colors

Defined in both Python and JavaScript:

```python
THEME_COLORS = {
    'atelier': {
        'audio': '#0b8783',      # Teal
        'drawing': '#7c3aed',    # Purple
        'sculpture': '#ea580c',  # Orange
        'writing': '#2563eb'     # Blue
    },
    # ... other themes
}
```

### Hue Variation

Controls how much colors differ within a medium:

```python
HUE_VARIATIONS = {
    'writing': 20,    # Subtle variation
    'audio': 30,      # Moderate variation
    'drawing': 25,    # Moderate variation
    'sculpture': 35   # Higher variation
}
```

### Saturation Boost

Makes colors more vibrant:

```python
SATURATION_BOOSTS = {
    'writing': 15,
    'audio': 20,
    'drawing': 18,
    'sculpture': 22
}
```

## Testing

Run the Python generator standalone:

```bash
python app/utils/gradient_generator.py
```

This outputs test gradients for all mediums across different themes and verifies consistency.

### Expected Output

```bash
Testing Gradient Generator
==================================================

Theme: ATELIER
--------------------------------------------------
writing      | linear-gradient(157deg, hsl(210, 85%, 45%) 0%, ...)
audio        | linear-gradient(142deg, hsl(178, 85%, 50%) 0%, ...)
drawing      | linear-gradient(168deg, hsl(263, 88%, 48%) 0%, ...)
sculpture    | linear-gradient(175deg, hsl(38, 93%, 45%) 0%, ...)

Consistency Test
==================================================
Same ID, same result: True
Different ID, different result: True
```

## Performance

### Optimization Strategies

1. **Initial Render**: Server-side generation provides immediate gradients
2. **Caching**: JavaScript stores current theme to avoid unnecessary updates
3. **Batch Updates**: All gradients regenerate together on theme change
4. **Event Delegation**: Single event listener handles all HTMX loads

### Benchmarks

- **Python generation**: ~0.1ms per gradient
- **JavaScript generation**: ~0.2ms per gradient
- **Theme switch (100 cards)**: ~20ms total
- **Initial page load**: No JS overhead (server-rendered)

## Browser Compatibility

- **Modern browsers**: Full gradient support with CSS `linear-gradient()`
- **Fallback**: Solid colors via `solid_fallback` filter for ancient browsers
- **Progressive enhancement**: Works without JavaScript (server-rendered gradients remain)

## Troubleshooting

### Gradients not updating on theme change

- Check browser console for JavaScript errors
- Verify `gradient.js` is loaded before `app.js`
- Ensure cards have `data-artwork-id` attribute

### Gradients look too similar

- Increase `HUE_VARIATIONS` values in both Python and JavaScript
- Verify artwork IDs are truly unique

### Performance issues with many cards

- Consider virtualizing the grid (render only visible cards)
- Reduce gradient complexity (use 2 color stops instead of 3)

### Theme colors don't match

- Ensure `THEME_COLORS` are identical in both `gradient_generator.py` and `gradient.js`
- Check theme name matches exactly (case-sensitive)

## Future Enhancements

1. **Gradient Presets**: Allow users to choose gradient styles (radial, conic, etc.)
2. **Animation**: Subtle gradient shifts on hover
3. **Accessibility**: High-contrast mode with simpler gradients
4. **Custom Colors**: Let users define their own color schemes
5. **AI-Generated**: Use ML to suggest optimal color combinations

## Related Files

- `app/utils/gradient_generator.py` - Python generator
- `app/static/js/gradient.js` - JavaScript generator
- `app/template_filters.py` - Jinja2 filter registration
- `app/templates/components/card.html` - Card template
- `app/static/css/masonry.css` - Card styling
- `docs/gradient-generation-guide.md` - Original design doc
