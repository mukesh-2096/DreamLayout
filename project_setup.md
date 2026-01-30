# 🚀 DreamLayout Project Setup Guide

Welcome to **DreamLayout**! DreamLayout is an AI-powered Architectural Co-pilot built with **FastAPI**. Follow these steps to set up the project on your local machine.

## 🏗️ Tech Stack
- **Backend:** FastAPI (Python 3.8+)
- **Frontend:** HTML5, Tailwind CSS, Jinja2 Templates
- **Database:** SQLite (Relational) & FAISS (Vector Index)
- **Image Hosting:** Cloudinary
- **AI Brain:** Gemini 2.5 Flash (via Google AI Studio)
- **AI Orchestration:** LangChain (LCEL)
- **Authentication:** Custom Session-based with FastAPI Middlewares

---

## 📋 Prerequisites
- **Python 3.8+** installed.
- **Git** for cloning the repository.
- A **Cloudinary Account** (Free tier) for image hosting.

---

## 🛠️ Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/DreamLayout.git
cd DreamLayout
```

### 2. Create a Virtual Environment
It's highly recommended to use a virtual environment.
```powershell
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1
```
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory. You can use `.env.example` as a template:
```bash
# Windows
copy .env.example .env
# Linux/macOS
cp .env.example .env
```

Open `.env` and fill in:
- **SECRET_KEY**: A random secret string for session security.
- **CLOUDINARY_URL**: Your Cloudinary connection string (or individual keys if configured that way).
  - `CLOUDINARY_CLOUD_NAME`
  - `CLOUDINARY_API_KEY`
  - `CLOUDINARY_API_SECRET`
- **GEMINI_API_KEY**: Your Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/).

---

## 🗄️ Database & Vector Index
The project uses **SQLite** for user data and **FAISS** for vector-based search.
- **SQLite**: `users.db` stores profile info.
- **FAISS**: `user_embeddings.index` and `user_id_mapping.pkl` handle the AI search indexing.
These are initialized automatically on the first run.

---

## 🏃‍♂️ Running the Project
Start the development server with auto-reload:
```bash
python run.py
```
Open your browser to: `http://127.0.0.1:5000`

---

## 📁 Key Directories
- `src/`: Backend logic (Routes, Models, Database).
- `templates/`: HTML Jinja2 templates (Modern UI with Tailwind CSS).
- `static/`: CSS, JS, and local images.
- `venv/`: Your Python virtual environment (Git-ignored).

---

## 🔍 Utilities
- **View Local Database**: `python view_database.py` (CLI tool to see registered users).
- **Check FAISS Index**: `python check_faiss.py` (Verified vector search status).

---

## 🛡️ Security Note
The `.env`, `users.db`, and FAISS index files are ignored by Git. **Never commit your credentials.**
