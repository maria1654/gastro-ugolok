from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

templates = Jinja2Templates(directory="templates")

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/admin"):
            role = request.session.get("role")
            admin_session_id = request.session.get("admin_session_id")
            
            if not all([role == "admin", admin_session_id]):
                return RedirectResponse(
                    url="/403",
                    status_code=303
                )

        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            if exc.status_code == 403:
                return RedirectResponse(
                    url="/403",
                    status_code=303
                )
            raise

async def get_current_user(request):
    """
    Получает информацию о текущем пользователе из сессии
    """
    username = request.session.get('user')
    role = request.session.get('role')
    session_id = request.session.get('session_id')
    
    if not all([username, role, session_id]):
        return None
        
    return {
        'username': username,
        'role': role,
        'session_id': session_id
    }

def setup_middleware(app):
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SESSION_SECRET_KEY"),
        session_cookie="session",
        max_age=int(os.getenv("SESSION_LIFETIME", 3600)),
        same_site=os.getenv("SAME_SITE_POLICY", "lax"),
        https_only=False,
        path="/",
    )