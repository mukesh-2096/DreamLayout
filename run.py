import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from src.app import app

if __name__ == "__main__":
    # Run FastAPI using uvicorn
    uvicorn.run("src.app:app", host="127.0.0.1", port=5000, reload=True)
