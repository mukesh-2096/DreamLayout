class User:
    """User model for authentication"""
    def __init__(self, id, name, email, about=None, profile_pic=None, location=None, user_key=None, password_hash=None):
        self.id = id
        self.name = name
        self.email = email
        self.about = about
        self.profile_pic = profile_pic
        self.location = location
        self.user_key = user_key
        self.password_hash = password_hash

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return str(self.id)
