from flask_login import UserMixin

class User(UserMixin):
    """User model for Flask-Login"""
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
