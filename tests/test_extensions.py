from app import extensions


def test_extensions_have_csrf_and_login_manager():
    assert hasattr(extensions, "csrf")
    assert hasattr(extensions, "login_manager")
    assert extensions.csrf is not None
    assert extensions.login_manager is not None
