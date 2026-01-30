from flask_login import UserMixin

class User(UserMixin):
    """User model for Flask-Login"""
    def __init__(self, id, name, email, about=None, profile_pic=None, location=None):
        self.id = id
        self.name = name
        self.email = email
        self.about = about
        self.profile_pic = profile_pic
        self.location = location
