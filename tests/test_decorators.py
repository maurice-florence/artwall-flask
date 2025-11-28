import pytest
from unittest.mock import patch
from flask import Flask, g
from app.utils.decorators import login_required


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test"
    # Register a minimal auth blueprint for testing
    from flask import Blueprint

    auth_bp = Blueprint("auth", __name__)

    @auth_bp.route("/login")
    def login():
        return "login page"

    app.register_blueprint(auth_bp, url_prefix="/auth")
    return app


def test_login_required_redirects_without_cookie(app):
    @login_required
    def protected():
        return "ok"

    with app.test_request_context("/"):
        # No session cookie
        resp = protected()
        assert resp.status_code == 302
        assert "/login" in resp.location


def test_login_required_valid_cookie(app):
    @login_required
    def protected():
        return "ok"

    with app.test_request_context("/", headers={"Cookie": "session=abc"}):
        with patch("app.utils.decorators.auth.verify_session_cookie") as mock_verify:
            mock_verify.return_value = {"uid": "user1"}
            resp = protected()
            assert resp == "ok"
            assert g.user["uid"] == "user1"


def test_login_required_invalid_cookie(app):
    @login_required
    def protected():
        return "ok"

    with app.test_request_context("/", headers={"Cookie": "session=bad"}):
        from firebase_admin import auth as firebase_auth

        with patch(
            "app.utils.decorators.auth.verify_session_cookie",
            side_effect=firebase_auth.InvalidSessionCookieError("bad cookie"),
        ):
            resp = protected()
            assert resp.status_code == 302
            assert "/login" in resp.location
