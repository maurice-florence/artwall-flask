/**
 * Dynamic Gradient Generator for Artwall Cards
 * Generates unique, theme-aware gradients based on artwork ID and medium
 */

// Theme color configurations matching Python gradient_generator.py
const THEME_COLORS = {
    'atelier': {
        'audio': '#0b8783',
        'drawing': '#7c3aed',
        'sculpture': '#ea580c',
        'writing': '#2563eb'
    },
    'blueprint': {
        'audio': '#1e40af',
        'drawing': '#7c3aed',
        'sculpture': '#ea580c',
        'writing': '#2563eb'
    },
    'dark': {
        'audio': '#0b8783',
        'drawing': '#7c3aed',
        'sculpture': '#ea580c',
        'writing': '#2563eb'
    },
    'teal': {
        'audio': '#0f766e',
        'drawing': '#7c3aed',
        'sculpture': '#ea580c',
        'writing': '#2563eb'
    },
    'nature': {
        'audio': '#16a34a',
        'drawing': '#7c3aed',
        'sculpture': '#ea580c',
        'writing': '#2563eb'
    },
    'earth': {
        'audio': '#92400e',
        'drawing': '#7c3aed',
        'sculpture': '#ea580c',
        'writing': '#2563eb'
    }
};

const HUE_VARIATIONS = {
    'writing': 20,
    'audio': 30,
    'drawing': 25,
    'sculpture': 35
};

const SATURATION_BOOSTS = {
    'writing': 5,
    'audio': 5,
    'drawing': 5,
    'sculpture': 5
};

/**
 * Simple hash function to convert string to number
 */
function hashStringToNumber(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
}

/**
 * Convert hex color to RGB
 */
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

/**
 * Convert RGB to HSL
 */
function rgbToHsl(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;
    
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;
    
    if (max === min) {
        h = s = 0;
    } else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
    }
    
    return {
        h: Math.round(h * 360),
        s: Math.round(s * 100),
        l: Math.round(l * 100)
    };
}

/**
 * Generate unique gradient for an artwork
 */
function generateGradient(artworkId, medium, theme = 'atelier') {
    // Get theme colors
    const themeColors = THEME_COLORS[theme] || THEME_COLORS['atelier'];
    const baseColor = themeColors[medium] || themeColors['drawing'];
    
    // Convert to HSL
    const rgb = hexToRgb(baseColor);
    if (!rgb) return null;
    
    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
    const themeH = hsl.h;
    const themeS = hsl.s;
    const themeL = hsl.l;
    
    // Get hash-based values
    const hashValue = hashStringToNumber(artworkId);
    
    // Configuration
    const hueVariation = HUE_VARIATIONS[medium] || 25;
    const saturationBoost = SATURATION_BOOSTS[medium] || 18;
    
    // Generate three color stops
    const hue1 = (themeH + (hashValue % hueVariation)) % 360;
    const hue2 = (hue1 + 25) % 360;
    const hue3 = (hue2 + 25) % 360;
    
    // Boost saturation
    const sat1 = Math.min(95, themeS + saturationBoost);
    const sat2 = Math.min(98, themeS + saturationBoost + 5);
    const sat3 = Math.min(95, themeS + saturationBoost + 3);
    
    // Adjust lightness
    const light1 = Math.max(35, Math.min(50, themeL - 5));
    const light2 = Math.max(40, Math.min(55, themeL));
    const light3 = Math.max(45, Math.min(60, themeL + 5));
    
    // Calculate angle
    const angle = (hashValue % 45) + 135;
    
    // Build gradient
    const color1 = `hsl(${hue1}, ${sat1}%, ${light1}%)`;
    const color2 = `hsl(${hue2}, ${sat2}%, ${light2}%)`;
    const color3 = `hsl(${hue3}, ${sat3}%, ${light3}%)`;
    
    return `linear-gradient(${angle}deg, ${color1} 0%, ${color2} 50%, ${color3} 100%)`;
}

/**
 * Update all card gradients based on current theme
 * Note: Only atelier theme uses dynamic gradients
 * Other themes use static backgrounds defined in themes.css
 */
function updateAllGradients() {
    const currentTheme = document.body.getAttribute('data-theme') || 'atelier';
    const cardFronts = document.querySelectorAll('.card-front[data-artwork-id]');
    
    console.log(`Theme: ${currentTheme} - ${cardFronts.length} cards`);
    
    // Only generate dynamic gradients for atelier theme
    // Other themes use static backgrounds from themes.css
    if (currentTheme !== 'atelier') {
        console.log('Using static theme backgrounds from CSS');
        // Remove inline styles to let CSS theme backgrounds take over
        cardFronts.forEach(cardFront => {
            cardFront.style.background = '';
        });
        return;
    }
    
    console.log(`Generating dynamic gradients for atelier theme`);
    
    cardFronts.forEach(cardFront => {
        const artworkId = cardFront.getAttribute('data-artwork-id');
        const card = cardFront.closest('.card');
        const medium = card.className.match(/card-(\w+)/)?.[1] || 'drawing';
        
        const gradient = generateGradient(artworkId, medium, currentTheme);
        if (gradient) {
            cardFront.style.background = gradient;
        }
    });
}

/**
 * Initialize gradient system
 */
function initGradients() {
    // Generate initial gradients
    updateAllGradients();
    
    // Listen for theme changes
    const themeSelector = document.getElementById('theme-selector');
    if (themeSelector) {
        themeSelector.addEventListener('change', function() {
            console.log('Theme changed, regenerating gradients...');
            updateAllGradients();
        });
    }
    
    // Also regenerate when new cards are added via HTMX
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.id === 'grid-container') {
            console.log('New cards loaded, generating gradients...');
            updateAllGradients();
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGradients);
} else {
    initGradients();
}
