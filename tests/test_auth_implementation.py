import unittest
from unittest.mock import patch
from flask import Flask
from flask_login import LoginManager, current_user


class TestAuthImplementation(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "test-secret"
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)

        # Manually register the request_loader we implemented
        # Since we can't easily import the decorated function from the factory,
        # we will replicate the logic or try to import the app factory if possible.
        # However, importing app factory might trigger firebase init.
        # Let's try to import the function if it was defined at module level,
        # but it's inside create_app.
        # So we need to mock the app creation or just test the logic in isolation if possible.

        # Better approach: Create a mock app using the actual factory but mock firebase
        pass

    @patch("app.services.firebase_service.init_firebase")
    @patch("firebase_admin.auth.verify_session_cookie")
    def test_request_loader_success(self, mock_verify, mock_init):
        # Setup mocks
        mock_init.return_value = None
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}

        from app import create_app

        app = create_app("testing")

        with app.test_request_context(headers={"Cookie": "session=valid-token"}):
            # Trigger user loading
            # Flask-Login's current_user will call the request_loader
            user = current_user._get_current_object()

            self.assertFalse(user.is_anonymous)
            self.assertEqual(user.id, "test-uid")
            self.assertEqual(user.email, "test@example.com")

    @patch("app.services.firebase_service.init_firebase")
    @patch("firebase_admin.auth.verify_session_cookie")
    def test_request_loader_failure(self, mock_verify, mock_init):
        from firebase_admin import auth

        mock_init.return_value = None
        mock_verify.side_effect = auth.InvalidSessionCookieError("Invalid cookie")

        from app import create_app

        app = create_app("testing")

        with app.test_request_context(headers={"Cookie": "session=invalid-token"}):
            user = current_user._get_current_object()
            self.assertTrue(user.is_anonymous)


if __name__ == "__main__":
    unittest.main()
