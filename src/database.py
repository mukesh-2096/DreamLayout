import sqlite3
import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from src.config import Config

# Initialize sentence transformer model
embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def init_faiss():
    """Initialize FAISS index"""
    if not os.path.exists(Config.FAISS_INDEX_PATH):
        index = faiss.IndexFlatL2(Config.EMBEDDING_DIMENSION)
        faiss.write_index(index, Config.FAISS_INDEX_PATH)
        with open(Config.USER_MAPPING_PATH, 'wb') as f:
            pickle.dump({}, f)

def load_faiss_index():
    """Load FAISS index"""
    return faiss.read_index(Config.FAISS_INDEX_PATH)

def load_user_mapping():
    """Load user ID mapping"""
    if os.path.exists(Config.USER_MAPPING_PATH):
        with open(Config.USER_MAPPING_PATH, 'rb') as f:
            return pickle.load(f)
    return {}

def save_user_mapping(mapping):
    """Save user ID mapping"""
    with open(Config.USER_MAPPING_PATH, 'wb') as f:
        pickle.dump(mapping, f)

def add_user_to_faiss(user_id, email, name):
    """Add user embedding to FAISS"""
    # Create user profile text for embedding
    user_text = f"{name} {email}"
    embedding = embedding_model.encode([user_text])[0]
    
    # Load index and mapping
    index = load_faiss_index()
    mapping = load_user_mapping()
    
    # Add embedding to index
    index.add(np.array([embedding], dtype=np.float32))
    
    # Update mapping
    mapping[index.ntotal - 1] = user_id
    
    # Save index and mapping
    faiss.write_index(index, Config.FAISS_INDEX_PATH)
    save_user_mapping(mapping)

def get_user_by_id(user_id):
    """Get user from database by ID"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def get_user_by_email(email):
    """Get user from database by email"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, password_hash FROM users WHERE email = ?', (email,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def create_user(name, email, password_hash):
    """Create new user in database"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                 (name, email, password_hash))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_user_projects(user_id, limit=6):
    """Return list of user's projects.

    This is a lightweight stub that returns project metadata.
    Currently returns an empty list by default. You can later
    implement a `projects` table and return real data.
    """
    # TODO: implement real projects table and query
    return []
