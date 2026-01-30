from fastapi import APIRouter, Request, Form, Depends, File, UploadFile, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import time
import cloudinary
import cloudinary.uploader
import cloudinary.api

from src.database import get_user_projects, update_user, delete_user_db
from src.config import Config
from src.fastapi_utils import flash, render_template

main_router = APIRouter(tags=["Main"])

def get_current_user_req(request: Request):
    if not request.state.user:
        raise HTTPException(status_code=303, detail="Not logged in", headers={"Location": "/login"})
    return request.state.user

@main_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render_template(request, "index.html")

@main_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login")
    projects = get_user_projects(request.state.user.id)
    return render_template(request, "dashboard.html", {"projects": projects})

@main_router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login")
    return render_template(request, "settings.html")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@main_router.post("/settings")
async def settings(
    request: Request,
    name: str = Form(...),
    about: str = Form(None),
    location: str = Form(None),
    profile_pic: UploadFile = File(None)
):
    if not request.state.user:
        return RedirectResponse(url="/login")
        
    current_user = request.state.user
    profile_pic_filename = current_user.profile_pic
    
    if profile_pic and profile_pic.filename:
        if allowed_file(profile_pic.filename):
            try:
                # Read file content
                content = await profile_pic.read()
                # Move image to a user-specific folder using their SPECIAL KEY
                user_folder = f"dreamlayout_profiles/u_{current_user.user_key}"
                upload_result = cloudinary.uploader.upload(
                    content,
                    folder=user_folder,
                    public_id="avatar",
                    overwrite=True,
                    invalidate=True
                )
                profile_pic_filename = upload_result['secure_url']
            except Exception as e:
                flash(request, f'Error uploading to Cloudinary: {str(e)}', 'error')
        else:
            flash(request, 'Invalid file format. Please upload PNG, JPG, or GIF.', 'error')
            return RedirectResponse(url="/settings", status_code=status.HTTP_303_SEE_OTHER)

    if not name:
        flash(request, 'Name is required.', 'error')
    else:
        if update_user(current_user.user_key, name, current_user.email, about, profile_pic_filename, location):
            flash(request, 'Settings updated successfully!', 'success')
        else:
            flash(request, 'Failed to update settings.', 'error')
            
    return RedirectResponse(url="/settings", status_code=status.HTTP_303_SEE_OTHER)

@main_router.post("/delete_account")
async def delete_account(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login")
    
    user_key = request.state.user.user_key
    try:
        # Delete user files from Cloudinary
        try:
            cloudinary.api.delete_resources_by_prefix(f"dreamlayout_profiles/u_{user_key}/")
            cloudinary.api.delete_folder(f"dreamlayout_profiles/u_{user_key}")
        except Exception as cloud_err:
            print(f"Cloudinary cleanup notice: {cloud_err}")

        # Delete from SQLite DB
        delete_user_db(user_key)
        
        # Clear session
        request.state.session.clear()
        
        flash(request, 'Your account and all associated data have been permanently deleted.', 'success')
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        flash(request, f'An error occurred: {str(e)}', 'error')
        return RedirectResponse(url="/settings", status_code=status.HTTP_303_SEE_OTHER)

# Add dummy routes for other links in templates to avoid 404
@main_router.get("/templates")
async def templates_dummy(request: Request):
    if not request.state.user:
        flash(request, 'Please login to view templates.', 'error')
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return render_template(request, "templates.html")

@main_router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login")
    return render_template(request, "profile.html")

@main_router.post("/profile")
async def profile_update(
    request: Request,
    name: str = Form(...),
    about: str = Form(None),
    location: str = Form(None)
):
    if not request.state.user:
        return RedirectResponse(url="/login")
        
    current_user = request.state.user
    
    if not name:
        flash(request, 'Name is required.', 'error')
    else:
        # Pass None for profile_pic to keep existing
        if update_user(current_user.user_key, name, current_user.email, about, None, location):
            flash(request, 'Profile updated successfully!', 'success')
        else:
            flash(request, 'Failed to update profile.', 'error')
            
    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)


@main_router.get("/favourites")
async def favourites_dummy(request: Request):
    return render_template(request, "favourites.html")
