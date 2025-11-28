from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from firebase_admin import auth
from datetime import timedelta, datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    """Renders the login page with the minimal JS SDK."""
    return render_template("auth/login.html")


@auth_bp.route("/session-login", methods=["POST"])
def session_login():
    """Exchanges ID Token for Session Cookie."""
    # 1. Get the ID token from the request body
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400

    id_token = request.json.get("idToken")
    if not id_token:
        return jsonify({"error": "Missing ID token"}), 400

    try:
        # 2. Create the session cookie
        # Set session expiration to 5 days
        expires_in = timedelta(days=5)
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)

        # 3. Create the response
        response = jsonify({"status": "success"})

        # 4. Set the cookie
        # Calculate exact expiration time for the browser cookie
        expires = datetime.now() + expires_in

        response.set_cookie(
            "session",
            session_cookie,
            expires=expires,
            httponly=True,  # Prevents JS access (XSS mitigation)
            secure=True,  # Only sent over HTTPS
            samesite="Lax",  # CSRF mitigation
        )
        return response

    except auth.InvalidIdTokenError:
        return jsonify({"error": "Invalid ID token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/logout")
def logout():
    response = redirect(url_for("auth.login"))
    response.set_cookie("session", expires=0)
    return response
