from fastapi import APIRouter, Request, Form, Depends, File, UploadFile, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import time
import json
import base64
import cloudinary
import cloudinary.uploader
import cloudinary.api

from src.database import (
    get_user_projects, update_user, delete_user_db, add_user_project, 
    get_project_by_id, soft_delete_project, restore_project, 
    hard_delete_project, get_user_archived_projects, update_project_status,
    get_favourite_projects, get_public_projects
)
from src.config import Config
from src.fastapi_utils import flash, render_template
from src.layout_generator import layout_generator

main_router = APIRouter(tags=["Main"])

@main_router.post("/api/generate-layout")
async def api_generate_layout(request: Request):
    if not request.state.user:
        return {"error": "Unauthorized"}, 401
    
    data = await request.json()
    venture_type = data.get("venture_type")
    area = data.get("area")
    dimensions = data.get("dimensions")
    user_prompt = data.get("prompt")
    
    try:
        result = layout_generator.generate_layout(venture_type, area, dimensions, user_prompt)
        
        # Handle multiple floors if present
        floors = result.get("floors", [])
        if floors:
            svg_content = floors[0].get("svg", "")
            rooms_data = json.dumps(floors) # Store all floors in rooms column
        else:
            svg_content = result.get("svg", "")
            rooms_data = json.dumps(result.get("rooms", []))

        # Upload SVG to Cloudinary
        cloudinary_url = None
        if svg_content:
            try:
                # Robust SVG normalization: Ensure required XML namespaces are present
                if 'xmlns=' not in svg_content.lower():
                    svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
                
                # Add XML declaration if missing to ensure proper processing
                if '<?xml' not in svg_content:
                    svg_content = '<?xml version="1.0" encoding="UTF-8"?>' + svg_content

                svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
                data_uri = f"data:image/svg+xml;base64,{svg_base64}"
                
                timestamp = int(time.time())
                project_slug = result.get("title", "layout").lower().replace(" ", "_")[:20]
                
                print(f"🔄 Syncing Preview to Cloudinary: project={project_slug}, user={request.state.user.user_key[:8]}...")
                
                upload_res = cloudinary.uploader.upload(
                    data_uri,
                    folder=f"dreamlayout_projects/u_{request.state.user.user_key}",
                    public_id=f"{project_slug}_prev_{timestamp}",
                    format="svg",
                    resource_type="image"
                )
                
                cloudinary_url = upload_res.get('secure_url')
                print(f"✅ Cloudinary Preview Success: {cloudinary_url}")
            except Exception as ce:
                print(f"❌ Cloudinary Preview Failed: {str(ce)}")

        # Save to database
        project_id = add_user_project(
            user_id=request.state.user.id,
            title=result.get("title", "New Proposal"),
            description=result.get("description", ""),
            thumbnail=cloudinary_url,
            svg_content=svg_content,
            rooms=rooms_data,
            design_philosophy=result.get("conversational_response", "")
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "layout": result,
            "cloudinary_url": cloudinary_url
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

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
    projects = get_user_projects(request.state.user.id, limit=100)
    # The template will handle slicing for the grid
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
async def templates_page(request: Request):
    public_projects = get_public_projects()
    return render_template(request, "templates.html", {"public_projects": public_projects})

@main_router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login")
    projects = get_user_projects(request.state.user.id, limit=100)
    return render_template(request, "profile.html", {"projects": projects})

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
async def favourites_page(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login")
    projects = get_favourite_projects(request.state.user.id)
    return render_template(request, "favourites.html", {"projects": projects})

@main_router.get("/my-projects")
async def my_projects(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login")
    projects = get_user_projects(request.state.user.id, limit=100)
    return render_template(request, "my_projects.html", {"projects": projects})

@main_router.post("/api/projects/bulk-action")
async def bulk_action(request: Request):
    if not request.state.user:
        return {"success": False, "error": "Unauthorized"}
    
    try:
        data = await request.json()
        project_ids = data.get("project_ids", [])
        action = data.get("action") # 'favourite' or 'public'
        value = data.get("value", 1) # 1 for public/favourite, 0 for private/unfavourite
        
        if not project_ids or action not in ['favourite', 'public']:
            return {"success": False, "error": "Invalid data"}
            
        field = "is_favourite" if action == "favourite" else "is_public"
        success = update_project_status(project_ids, field, value, request.state.user.id)
        
        if not success:
            return {"success": False, "error": "Access denied. You can only manage your own projects."}
            
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@main_router.get("/project/{project_id}")
async def view_project(request: Request, project_id: int):
    if not request.state.user:
        return RedirectResponse(url="/login")
    
    project = get_project_by_id(project_id)
    if not project or project['user_id'] != request.state.user.id:
        flash(request, "Project not found or access denied.", "error")
        return RedirectResponse(url="/dashboard")
    
    # Parse rooms JSON
    try:
        project['rooms'] = json.loads(project['rooms'])
    except:
        project['rooms'] = []
        
    return render_template(request, "project_view.html", {"project": project})

@main_router.get("/archive")
async def archive_view(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login")
    archived_projects = get_user_archived_projects(request.state.user.id)
    return render_template(request, "archive.html", {"projects": archived_projects})

@main_router.post("/api/project/{project_id}/delete")
async def api_soft_delete(request: Request, project_id: int):
    if not request.state.user:
        return {"error": "Unauthorized"}, 401
    
    project = get_project_by_id(project_id)
    if not project or project['user_id'] != request.state.user.id:
        return {"error": "Access denied"}, 403
    
    soft_delete_project(project_id)
    return {"success": True}

@main_router.post("/api/project/{project_id}/restore")
async def api_restore(request: Request, project_id: int):
    if not request.state.user:
        return {"error": "Unauthorized"}, 401
    
    # Check project ownership (even if archived)
    project = get_project_by_id(project_id)
    if not project or project['user_id'] != request.state.user.id:
        return {"error": "Access denied"}, 403
    
    restore_project(project_id)
    return {"success": True}

@main_router.post("/api/project/{project_id}/permanent-delete")
async def api_hard_delete(request: Request, project_id: int):
    if not request.state.user:
        return {"error": "Unauthorized"}, 401
    
    project = get_project_by_id(project_id)
    if not project or project['user_id'] != request.state.user.id:
        return {"error": "Access denied"}, 403
    
    hard_delete_project(project_id)
    return {"success": True}

@main_router.get("/generate", response_class=HTMLResponse)
async def generate_page(request: Request):
    if not request.state.user:
        return RedirectResponse(url="/login")
    return render_template(request, "generate.html")

@main_router.post("/api/generate-preview")
async def api_generate_preview(request: Request):
    if not request.state.user:
        return {"error": "Unauthorized"}, 401
    
    data = await request.json()
    venture_type = data.get("venture_type")
    area = data.get("area")
    dimensions = data.get("dimensions")
    user_prompt = data.get("prompt")
    
    try:
        # Generate layout using Gemini but DO NOT save to database yet
        result = layout_generator.generate_layout(venture_type, area, dimensions, user_prompt)
        return {
            "success": True,
            "layout": result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@main_router.post("/api/save-project")
async def api_save_project(request: Request):
    if not request.state.user:
        return {"error": "Unauthorized"}, 401
    
    data = await request.json()
    layout = data.get("layout")
    if not layout:
        return {"error": "No layout data provided"}, 400
        
    try:
        # Handle multiple floors if present
        floors = layout.get("floors", [])
        if floors:
            svg_content = floors[0].get("svg", "")
            rooms_data = json.dumps(floors) # Store all floors in rooms column
        else:
            svg_content = layout.get("svg", "")
            rooms_data = json.dumps(layout.get("rooms", []))

        cloudinary_url = None
        
        # Upload to Cloudinary
        # Upload to Cloudinary
        if svg_content:
            try:
                # Robust SVG normalization: Ensure required XML namespaces are present
                if 'xmlns=' not in svg_content.lower():
                    svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
                
                # Add XML declaration if missing to ensure proper processing
                if '<?xml' not in svg_content:
                    svg_content = '<?xml version="1.0" encoding="UTF-8"?>' + svg_content

                svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
                data_uri = f"data:image/svg+xml;base64,{svg_base64}"
                
                timestamp = int(time.time())
                project_slug = layout.get("title", "layout").lower().replace(" ", "_")[:20]
                
                print(f"🔄 Syncing to Cloudinary: project={project_slug}, user={request.state.user.user_key[:8]}...")
                
                upload_res = cloudinary.uploader.upload(
                    data_uri,
                    folder=f"dreamlayout_projects/u_{request.state.user.user_key}",
                    public_id=f"{project_slug}_{timestamp}",
                    format="svg",
                    resource_type="image"
                )
                
                cloudinary_url = upload_res.get('secure_url')
                print(f"✅ Cloudinary Sync Success: {cloudinary_url}")
            except Exception as ce:
                print(f"❌ Cloudinary Sync Failed: {str(ce)}")
                # Continue saving the project even if upload fails

        # Save to database
        project_id = add_user_project(
            user_id=request.state.user.id,
            title=layout.get("title", "New Proposal"),
            description=layout.get("description", ""),
            thumbnail=cloudinary_url,
            svg_content=svg_content,
            rooms=rooms_data,
            design_philosophy=layout.get("conversational_response", ""),
            design_code=layout.get("design_code")
        )
        
        return {
            "success": True,
            "project_id": project_id
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
