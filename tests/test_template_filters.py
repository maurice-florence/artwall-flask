from app.template_filters import gradient_filter, solid_fallback_filter


def test_gradient_filter():
    g = gradient_filter("id-1", "writing", "atelier")
    assert g.startswith("linear-gradient(")


def test_solid_fallback_filter():
    assert solid_fallback_filter("audio").startswith("#")
    assert solid_fallback_filter("drawing").startswith("#")
    assert solid_fallback_filter("sculpture").startswith("#")
    assert solid_fallback_filter("writing").startswith("#")
    assert solid_fallback_filter("unknown").startswith("#")
