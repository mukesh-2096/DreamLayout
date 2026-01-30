# 🚀 DreamLayout Project Setup Guide

Welcome to **DreamLayout**! Follow these steps to set up the project on your local machine.

## 📋 Prerequisites
- **Python 3.8+** installed on your system.
- **Git** for cloning the repository.
- A **Cloudinary Account** (Free tier works perfectly) for image hosting.

---

## 🛠️ Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/DreamLayout.git
cd DreamLayout
```

### 2. Create a Virtual Environment
It's highly recommended to use a virtual environment to keep dependencies isolated.
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
Create a `.env` file in the root directory by copying the example:
```bash
cp .env.example .env
```

Now, open `.env` and fill in your details:
- **SECRET_KEY**: Any random long string for session security.
- **Cloudinary Keys**: Log in to your [Cloudinary Dashboard](https://cloudinary.com/console) and copy your `Cloud Name`, `API Key`, and `API Secret`.

---

## 🗄️ Database Initialization
The project uses **SQLite** (for user data) and **FAISS** (for AI vector search). These will be automatically initialized when you first run the app, but you can also run:
```bash
# This creates users.db and indexing files if they don't exist
python run.py
```

---

## 🏃‍♂️ Running the Project
Once configured, start the development server:
```bash
python run.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 🔍 Database Troubleshooting
If you want to view the users currently in your local database, you can use the built-in utility:
```bash
python view_database.py
```

## ☁️ Cloudinary Structure
The project automatically creates a folder named `dreamlayout_profiles` in your Cloudinary account. Each user's data is isolated in a subfolder named `u_<unique_id>`, ensuring maximum privacy and data integrity.

---

## 🛡️ Security Note
The `.env` file and `users.db` are strictly ignored by Git to prevent your private keys and user data from being exposed on GitHub. **Never commit your `.env` file.**
