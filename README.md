# DreamLayout

DreamLayout is an AI-powered architectural co-pilot that transforms minimal user inputs—such as total area, venture type (office, home, etc.), user requirements, and an optional target budget—into an intelligent design and a realistic construction cost plan. 

## Features
- Generate intelligent designs based on user inputs and venture type.
- Provide realistic construction cost plans.
- View previously designed layouts for reference.

## How It Works
1. Input your requirements: total area, venture type, and other preferences.
2. (Optional) Specify a target budget.
3. DreamLayout generates a tailored design and cost plan.
4. Browse and use previously designed layouts for inspiration.

## Tech Stack
- **Backend**: Flask
- **Authentication**: Flask-Login
- **AI Brain**: Gemini 3 API (planned)
- **AI Orchestration**: LangChain (planned)
- **Vector DB**: FAISS with Sentence Transformers
- **Database**: SQLite
- **Cost Estimation**: Pandas, NumPy (planned)
- **Frontend**: HTML + Tailwind CSS
- **Interactivity**: Vanilla JavaScript

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd DreamLayout
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Update the `SECRET_KEY` with a secure random string
   ```bash
   copy .env.example .env  # On Windows
   # cp .env.example .env  # On Mac/Linux
   ```

5. **Run the application**
   ```bash
   python src/app.py
   ```

6. **Access the app**
   - Open browser: `http://localhost:5000`

## View User Data

```bash
python view_users.py
```

## Security Notes ⚠️
**IMPORTANT: Before pushing to GitHub, ensure these are hidden:**
- ❌ `.env` file (contains SECRET_KEY)
- ❌ Database files (`users.db`, `*.index`, `*.pkl`)
- ❌ `__pycache__` folders
- ✅ Use `.gitignore` (already created)
- ✅ Only commit `.env.example` (not `.env`)

## What to Hide (Like MongoDB URI in MERN)
In MERN you hide MongoDB cluster links. In this project:
- **SECRET_KEY** in `.env` (like JWT secret)
- **Database files** (like MongoDB data)
- **API keys** when added (Gemini API, etc.)

## Tech Stack
- **Backend**: FastAPI
- **AI Brain**: Gemini 3 API
- **AI Orchestration**: LangChain
- **Logic Engine**: Custom Python Rules
- **Cost Estimation**: Pandas, NumPy
- **Database**: SQLite, Faiss (Vector DB)
- **Frontend**: HTML + Tailwind CSS
- **Interactivity**: Vanilla JavaScript

## Project Structure
- `src`: Contains the source code for the application.
- `tests`: Includes test files to ensure the application works as expected.
- `assets`: Stores static assets like images and styles.
- `docs`: Contains documentation for the project.

## Getting Started
To get started with DreamLayout, clone the repository and explore the `src` folder to begin development.

## License
This project is licensed under the MIT License.

