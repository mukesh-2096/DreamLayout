from flask import Flask
from flask_login import LoginManager
from src.config import Config
from src.database import get_user_by_id
from src.models import User
from src.routes import auth_bp
from src.main_routes import main_bp

def create_app():
    """Application factory pattern"""
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )
    
    # Load configuration
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        user_data = get_user_by_id(user_id)
        if user_data:
            return User(user_data[0], user_data[1], user_data[2])
        return None
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app

