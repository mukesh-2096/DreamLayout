import os
import time
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeSerializer

from src.config import Config
from src.database import get_user_by_id, init_db, init_faiss
from src.models import User
from src.fastapi_utils import SessionManager, get_flashed_messages, current_user_func, url_for

def create_app():
    # Initialize Databases
    init_db()
    init_faiss()

    app = FastAPI(title="DreamLayout")

    # Static files & Templates
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
    
    # Session Manager
    session_manager = SessionManager(Config.SECRET_KEY)

    # Inject global functions into Jinja2
    templates.env.globals['get_flashed_messages'] = get_flashed_messages
    templates.env.globals['current_user'] = current_user_func
    templates.env.globals['url_for'] = url_for

    @app.middleware("http")
    async def session_middleware(request: Request, call_next):
        # 1. Load Session
        request.state.session = session_manager.get_session(request)
        
        # 2. Identify User
        user_id = request.state.session.get("user_id")
        request.state.user = None
        if user_id:
            user_data = get_user_by_id(user_id)
            if user_data:
                # SELECT id, name, email, about, profile_pic, location, user_key FROM users
                request.state.user = User(
                    user_data[0], user_data[1], user_data[2], 
                    about=user_data[3], profile_pic=user_data[4], 
                    location=user_data[5], user_key=user_data[6]
                )
        
        response = await call_next(request)
        
        # 3. Save Session back to cookie
        session_manager.save_session(response, request.state.session)
        return response

    # Attach templates to app for routers to use
    app.state.templates = templates

    # Include Routers
    from src.routes import auth_router
    from src.main_routes import main_router
    
    app.include_router(auth_router)
    app.include_router(main_router)

    return app, templates

app, templates = create_app()

