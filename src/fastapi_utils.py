import json
import base64
from typing import Optional, List, Tuple
from fastapi import Request, Response
from itsdangerous import URLSafeSerializer, BadSignature
from src.config import Config

class SessionManager:
    def __init__(self, secret_key: str):
        self.serializer = URLSafeSerializer(secret_key)

    def get_session(self, request: Request) -> dict:
        cookie = request.cookies.get("session_id")
        if not cookie:
            return {}
        try:
            return self.serializer.loads(cookie)
        except BadSignature:
            return {}

    def save_session(self, response: Response, session_data: dict):
        token = self.serializer.dumps(session_data)
        response.set_cookie(
            key="session_id",
            value=token,
            httponly=True,
            max_age=3600 * 24 * 7, # 7 days
            samesite="lax"
        )

def flash(request: Request, message: str, category: str = "info"):
    """Mimic Flask's flash() functionality"""
    session = getattr(request.state, "session", {})
    if "_flashes" not in session:
        session["_flashes"] = []
    session["_flashes"].append((category, message))
    request.state.session = session

from jinja2 import pass_context

@pass_context
def get_flashed_messages(context: dict, with_categories: bool = False):
    """Mimic Flask's get_flashed_messages() for Jinja2"""
    request = context.get("request")
    if not request:
        return []
    session = getattr(request.state, "session", {})
    flashes = session.pop("_flashes", [])
    request.state.session = session
    
    if with_categories:
        return flashes
    return [msg for cat, msg in flashes]

@pass_context
def url_for(context: dict, name: str, **path_params):
    """Mimic Flask's url_for()"""
    request = context.get("request")
    if not request:
        return ""
    return str(request.url_for(name, **path_params))

@pass_context
def current_user_func(context: dict):
    """Mimic current_user for templates"""
    request = context.get("request")
    return getattr(request.state, "user", None)

def render_template(request: Request, template_name: str, context: dict = {}):
    """Helper to render templates with common context"""
    templates = request.app.state.templates
    full_context = {
        "request": request,
        "current_user": getattr(request.state, "user", None),
        "get_flashed_messages": get_flashed_messages,
        "url_for": url_for,
        **context
    }
    return templates.TemplateResponse(template_name, full_context)



