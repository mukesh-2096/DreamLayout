import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.database import init_db, init_faiss
from src.app import create_app

if __name__ == "__main__":
    # Initialize databases
    init_db()
    init_faiss()
    
    # Create and run app
    app = create_app()
    app.run(debug=Config.DEBUG)
