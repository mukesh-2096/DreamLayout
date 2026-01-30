import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    
    # Database paths
    DB_PATH = os.getenv('DB_PATH', 'users.db')
    FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', 'user_embeddings.index')
    USER_MAPPING_PATH = os.getenv('USER_MAPPING_PATH', 'user_id_mapping.pkl')
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Embedding model
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    EMBEDDING_DIMENSION = 384
    
    # Upload Settings
    UPLOAD_FOLDER = 'static/uploads/profiles'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', 'dys7uqgs8')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '499189479929149')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', 'EpzRI8Q9EyACpEugEFd97id3XIY')
    


