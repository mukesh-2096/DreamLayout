# ✨ DreamLayout

DreamLayout is a premium AI-powered Architectural Co-pilot designed to transform abstract ideas into production-ready layout blueprints. Built with **FastAPI** and **Gemini 2.5 Flash**, it offers a seamless experience for homeowners, office managers, and retail designers to visualize their space in seconds.

---

## 🏗️ Core Features
- **Intelligent Architectural Brain**: Powered by **Gemini 2.5 Flash** and **LangChain (LCEL)** to generate high-fidelity floor plans.
- **Interactive Site Sketching**: Draw your site's unique shape on our custom digital canvas and watch the AI adapt to your dimensions.
- **SVG Blueprint Generation**: Receive clean, professional, and scalable SVG vector floor plans ready for review.
- **Design Philosophy**: Gemini doesn't just design; it explains its architectural reasoning and room optimization strategy.
- **Vector Search Engine**: Powered by **FAISS** and **Sentence Transformers** for advanced user profile indexing and future layout similarity matching.

---

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python 3.8+)
- **AI Brain**: Google Gemini 2.5 Flash
- **AI Orchestration**: LangChain (LCEL approach)
- **Vector DB**: FAISS (L2 Index)
- **Primary Database**: SQLite
- **Frontend**: HTML5, Tailwind CSS, Jinja2
- **Interactivity**: Vanilla JavaScript (Canvas API for site sketching)
- **Image Hosting**: Cloudinary

---

## 🚀 Quick Setup

1. **Clone & Enter**
   ```bash
   git clone <your-repo-url>
   cd DreamLayout
   ```

2. **Virtual Environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1 # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Fill in your `SECRET_KEY`, `CLOUDINARY_URL`, and `GEMINI_API_KEY`.

5. **Run the Application**
   ```bash
   python run.py
   ```
   *Access at: `http://localhost:5000`*

---

## 📁 Project Structure
- `src/`: Core logic, database handlers, and AI orchestration.
- `templates/`: Premium UI components and pages using Jinja2 & Tailwind.
- `static/`: Assets and styles.
- `project_setup.md`: Detailed step-by-step setup for new developers.

---

## 🛡️ Security & Privacy
DreamLayout is designed with privacy-first principles:
- **Environment Safety**: Sensitive keys are managed via `.env` and excluded from Git.
- **Local Vectors**: FAISS indices and mapping files are stored locally and never pushed to public repositories.
- **Secure Sessions**: User sessions are handled with signed cookies via `itsdangerous`.

---

## ⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.
