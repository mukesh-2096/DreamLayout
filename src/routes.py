from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

from src.database import get_user_by_email, create_user, add_user_to_faiss
from src.models import User
from src.fastapi_utils import flash, render_template

auth_router = APIRouter(tags=["Authentication"])

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return render_template(request, "login.html")

@auth_router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), remember: str = Form(None)):
    user_data = get_user_by_email(email)
    
    if user_data and check_password_hash(user_data[3], password):
        # user_data: (id, name, email, password_hash, about, profile_pic, location, user_key)
        request.state.session["user_id"] = user_data[0]
        request.state.session["_permanent"] = (remember == "on")
        flash(request, 'Login successful!', 'success')
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    else:
        flash(request, 'Invalid email or password', 'error')
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@auth_router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return render_template(request, "signup.html")

@auth_router.post("/signup")
async def signup(
    request: Request, 
    name: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...), 
    confirm_password: str = Form(...)
):
    # Validate password length
    if len(password) < 6:
        flash(request, 'Password must be at least 6 characters long', 'error')
        return RedirectResponse(url="/signup", status_code=status.HTTP_303_SEE_OTHER)
        
    # Validate passwords match
    if password != confirm_password:
        flash(request, 'Passwords do not match', 'error')
        return RedirectResponse(url="/signup", status_code=status.HTTP_303_SEE_OTHER)
    
    password_hash = generate_password_hash(password)
    
    try:
        user_id = create_user(name, email, password_hash)
        add_user_to_faiss(user_id, email, name)
        flash(request, 'Account created successfully! Please login.', 'success')
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    except sqlite3.IntegrityError:
        flash(request, 'Email already exists', 'error')
        return RedirectResponse(url="/signup", status_code=status.HTTP_303_SEE_OTHER)

@auth_router.get("/logout")
async def logout(request: Request):
    request.state.session.clear()
    flash(request, 'Logged out successfully', 'success')
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session_id")
    return response
