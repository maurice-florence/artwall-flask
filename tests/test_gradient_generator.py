from app.utils.gradient_generator import generate_gradient, generate_gradient_inline, get_solid_fallback

def test_generate_gradient_consistency():
    g1 = generate_gradient('id-1', 'writing', 'atelier')
    g2 = generate_gradient('id-1', 'writing', 'atelier')
    assert g1 == g2
    g3 = generate_gradient('id-2', 'writing', 'atelier')
    assert g1 != g3

def test_generate_gradient_different_mediums():
    g_audio = generate_gradient('id-x', 'audio', 'atelier')
    g_drawing = generate_gradient('id-x', 'drawing', 'atelier')
    g_sculpture = generate_gradient('id-x', 'sculpture', 'atelier')
    g_writing = generate_gradient('id-x', 'writing', 'atelier')
    assert len({g_audio, g_drawing, g_sculpture, g_writing}) == 4

def test_generate_gradient_inline():
    result = generate_gradient_inline('id-1', 'writing', 'atelier')
    assert result.startswith('linear-gradient(')

def test_get_solid_fallback():
    assert get_solid_fallback('audio').startswith('#')
    assert get_solid_fallback('drawing').startswith('#')
    assert get_solid_fallback('sculpture').startswith('#')
    assert get_solid_fallback('writing').startswith('#')
    assert get_solid_fallback('unknown').startswith('#')
