import sqlite3
import faiss
import numpy as np
import pickle
import os
import uuid
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
            user_key TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            about TEXT,
            profile_pic TEXT,
            location TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            thumbnail TEXT,
            svg_content TEXT,
            rooms TEXT,
            design_philosophy TEXT,
            is_deleted INTEGER DEFAULT 0,
            deleted_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Migration: Check if columns exist
    for col in ['about', 'profile_pic', 'location', 'user_key']:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
            if col == 'user_key':
                # Populate existing users with a key
                cursor.execute("SELECT id FROM users")
                for row in cursor.fetchall():
                    new_key = str(uuid.uuid4())
                    cursor.execute("UPDATE users SET user_key = ? WHERE id = ?", (new_key, row[0]))
        except sqlite3.OperationalError:
            pass

    # Migration for projects: add is_deleted, deleted_at, is_favourite, is_public
    for col, type_info in [
        ('is_deleted', 'INTEGER DEFAULT 0'), 
        ('deleted_at', 'TIMESTAMP'),
        ('is_favourite', 'INTEGER DEFAULT 0'),
        ('is_public', 'INTEGER DEFAULT 0'),
        ('design_code', 'TEXT')
    ]:
        try:
            cursor.execute(f"ALTER TABLE projects ADD COLUMN {col} {type_info}")
        except sqlite3.OperationalError:
            pass
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
    cursor.execute('SELECT id, name, email, about, profile_pic, location, user_key FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def get_user_by_email(email):
    """Get user from database by email"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, password_hash, about, profile_pic, location, user_key FROM users WHERE email = ?', (email,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def create_user(name, email, password_hash):
    """Create new user in database with a unique user_key"""
    user_key = str(uuid.uuid4())
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, email, password_hash, user_key) VALUES (?, ?, ?, ?)',
                 (name, email, password_hash, user_key))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id
def update_user(user_id, name, email, about, profile_pic=None, location=None):
    """Update user information in database"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    
    # Identify the target user_key correctly
    target_key = user_id
    if not (isinstance(user_id, str) and '-' in user_id):
        # If passed an integer ID, look up the key
        user_data = get_user_by_id(user_id)
        if user_data:
            target_key = user_data[6]
        else:
            conn.close()
            return False

    if profile_pic:
        cursor.execute('UPDATE users SET name = ?, email = ?, about = ?, profile_pic = ?, location = ? WHERE user_key = ?',
                     (name, email, about, profile_pic, location, target_key))
    else:
        cursor.execute('UPDATE users SET name = ?, email = ?, about = ?, location = ? WHERE user_key = ?',
                     (name, email, about, location, target_key))
    conn.commit()
    conn.close()
    return True


def delete_user_db(user_key):
    """Delete user from database by user_key"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE user_key = ?', (user_key,))
    conn.commit()
    conn.close()
    return True

def add_user_project(user_id, title, description, thumbnail, svg_content, rooms, design_philosophy, design_code=None):
    """Add a new project to the database"""
    if not design_code:
        import random
        import string
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        design_code = f"DL-{suffix}"
        
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO projects (user_id, title, description, thumbnail, svg_content, rooms, design_philosophy, design_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, title, description, thumbnail, svg_content, rooms, design_philosophy, design_code))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def get_user_projects(user_id, limit=6):
    """Return list of user's projects"""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, description, thumbnail, svg_content, rooms, design_philosophy, updated_at, is_favourite, is_public 
        FROM projects 
        WHERE user_id = ? AND is_deleted = 0
        ORDER BY updated_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return projects

def get_favourite_projects(user_id):
    """Return list of user's favourite projects"""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, description, thumbnail, svg_content, rooms, updated_at, design_code 
        FROM projects 
        WHERE user_id = ? AND is_deleted = 0 AND is_favourite = 1
        ORDER BY updated_at DESC
    ''', (user_id,))
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return projects

def get_public_projects(limit=50):
    """Return list of public templates"""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, description, thumbnail, svg_content, rooms, updated_at, design_code 
        FROM projects 
        WHERE is_public = 1 AND is_deleted = 0
        ORDER BY updated_at DESC
        LIMIT ?
    ''', (limit,))
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return projects

def update_project_status(project_ids, status_field, value, user_id):
    """Update status field (is_favourite/is_public) for multiple projects belonging to user_id"""
    if not project_ids:
        return True
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    placeholders = ','.join(['?'] * len(project_ids))
    # Add user_id check for security
    cursor.execute(f'''
        UPDATE projects 
        SET {status_field} = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id IN ({placeholders}) AND user_id = ?
    ''', [value] + project_ids + [user_id])
    
    updated_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    # Return true only if all projects were updated (means user owned all of them)
    return updated_count == len(project_ids)

def get_project_by_id(project_id):
    """Get a single project by ID"""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, user_id, title, description, thumbnail, svg_content, rooms, design_philosophy, updated_at, design_code 
        FROM projects 
        WHERE id = ?
    ''', (project_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_project(project_id, title, description):
    """Update project metadata"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects 
        SET title = ?, description = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (title, description, project_id))
    conn.commit()
    conn.close()
    return True

def soft_delete_project(project_id):
    """Move project to recycle bin"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects 
        SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (project_id,))
    conn.commit()
    conn.close()
    return True

def restore_project(project_id):
    """Restore project from recycle bin"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects 
        SET is_deleted = 0, deleted_at = NULL 
        WHERE id = ?
    ''', (project_id,))
    conn.commit()
    conn.close()
    return True

def hard_delete_project(project_id):
    """Permanently delete project"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    return True

def get_user_archived_projects(user_id):
    """Get soft-deleted projects for a user"""
    # Auto-purge old items first
    purge_old_archived_projects()
    
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, description, thumbnail, svg_content, rooms, design_philosophy, deleted_at 
        FROM projects 
        WHERE user_id = ? AND is_deleted = 1
        ORDER BY deleted_at DESC
    ''', (user_id,))
    projects = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return projects

def purge_old_archived_projects():
    """Permanently delete projects older than 5 days in recycle bin"""
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    # SQLITE logic for 5 days: datetime('now', '-5 days')
    cursor.execute("DELETE FROM projects WHERE is_deleted = 1 AND deleted_at < datetime('now', '-5 days')")
    conn.commit()
    conn.close()
