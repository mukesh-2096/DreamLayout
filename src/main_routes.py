from flask import Blueprint, render_template
from flask_login import login_required, current_user
from src.database import get_user_projects

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    """Home page"""
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard page - passes user projects to template."""
    projects = get_user_projects(current_user.id)
    return render_template("dashboard.html", projects=projects)
