from flask_login import UserMixin


class User(UserMixin):
    """
    User class for Flask-Login integration.
    Represents a user authenticated via Firebase.
    """

    def __init__(self, uid, email=None, display_name=None):
        self.id = uid
        self.email = email
        self.display_name = display_name

    def __repr__(self):
        return f"<User {self.id}>"
