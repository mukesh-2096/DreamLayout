from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from src.models import User
from src.database import get_user_by_email, create_user, add_user_to_faiss

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Query user from database
        user_data = get_user_by_email(email)
        
        if user_data and check_password_hash(user_data[3], password):
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for("main.dashboard"))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for("auth.login"))
    
    return render_template("login.html")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup"""
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for("auth.signup"))
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        try:
            # Insert user into database
            user_id = create_user(name, email, password_hash)
            
            # Add user to FAISS vector database
            add_user_to_faiss(user_id, email, name)
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for("auth.login"))
        
        except sqlite3.IntegrityError:
            flash('Email already exists', 'error')
            return redirect(url_for("auth.signup"))
    
    return render_template("signup.html")

@auth_bp.route("/logout")
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for("main.home"))
