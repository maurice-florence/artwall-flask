from functools import wraps
from flask import request, redirect, url_for, g
from firebase_admin import auth


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_cookie = request.cookies.get("session")

        if not session_cookie:
            # No cookie, redirect to login
            return redirect(url_for("auth.login"))

        try:
            # Verify the session cookie
            # check_revoked=True checks if the user's session was revoked in Firebase console
            decoded_claims = auth.verify_session_cookie(
                session_cookie, check_revoked=True
            )

            # Attach the user info to the global request context 'g'
            g.user = decoded_claims

        except auth.InvalidSessionCookieError:
            # Cookie is invalid or expired
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function
