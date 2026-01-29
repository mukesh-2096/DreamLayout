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
