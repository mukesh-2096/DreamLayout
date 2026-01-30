import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from src.database import get_user_projects, update_user
from src.config import Config
import cloudinary
import cloudinary.uploader

# Configure Cloudinary
cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

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

@main_bp.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        about = request.form.get('about')
        location = request.form.get('location')
        
        # Simple validation
        if not name:
            flash('Name is required.')
        else:
            # We use current_user.email to ensure the email never changes
            update_user(current_user.id, name, current_user.email, about, current_user.profile_pic, location)
            flash('Profile updated successfully!')
            return redirect(url_for('main.profile'))
            
    return render_template("profile.html")
@main_bp.route("/templates")
@login_required
def templates_page():
    """Reference templates page"""
    return render_template("templates.html")

@main_bp.route("/favourites")
@login_required
def favourites_page():
    """User favourites page"""
    return render_template("favourites.html")

@main_bp.route("/settings", methods=['GET', 'POST'])
@login_required
def settings_page():
    """User settings page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        about = request.form.get('about')
        location = request.form.get('location')
        
        # Handle Profile Picture Upload
        profile_pic_filename = current_user.profile_pic
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '' and allowed_file(file.filename):
                try:
                    # Upload to Cloudinary
                    upload_result = cloudinary.uploader.upload(
                        file,
                        folder="dreamlayout_profiles",
                        public_id=f"user_{current_user.id}"
                    )
                    profile_pic_filename = upload_result['secure_url']
                except Exception as e:
                    flash(f'Error uploading to Cloudinary: {str(e)}')
                    # Fallback to current pic if upload fails
                    profile_pic_filename = current_user.profile_pic
        
        # Simple validation
        if not name:
            flash('Name is required.')
        else:
            # We use current_user.email to ensure the email never changes
            update_user(current_user.id, name, current_user.email, about, profile_pic_filename, location)
            flash('Settings updated successfully!')
            return redirect(url_for('main.settings_page'))
            
    return render_template("settings.html")



