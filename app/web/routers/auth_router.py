from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import os
import time

from app.auth import authenticate_user, create_user

templates = Jinja2Templates(directory="templates")
router = APIRouter()

def get_session_data(request: Request):
    username = request.session.get('user')
    cookies_accepted = request.session.get('cookies_accepted', False)
    return {'user': username, 'cookies_accepted': cookies_accepted}

@router.get("/registration")
async def registration_form(request: Request, session_data: dict = Depends(get_session_data)):
    return templates.TemplateResponse("registration.html", {"request": request, **session_data})

@router.post("/registration")
async def registration(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    session_data: dict = Depends(get_session_data)
):
    if password != confirm_password:
        return templates.TemplateResponse("registration.html", {"request": request, **session_data, "error": "Пароли не совпадают"})
    if create_user(username, email, password):
        return RedirectResponse(url='/login', status_code=303)
    else:
        return templates.TemplateResponse("registration.html", {"request": request, **session_data, "error": "Пользователь уже существует"})

@router.get("/login")
async def login_form(request: Request, session_data: dict = Depends(get_session_data)):
    return templates.TemplateResponse("login.html", {"request": request, **session_data})

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session_data: dict = Depends(get_session_data)
):
    user = authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, **session_data, "error": "Неверные учетные данные"}
        )

    # Очищаем старую сессию
    request.session.clear()
    
    # Создаем новую сессию с базовыми данными
    session_id = os.urandom(32).hex()
    request.session['user'] = user.username
    request.session['role'] = user.role
    request.session['session_id'] = session_id
    request.session['session_start'] = time.time()
    
    # Дополнительные данные для админов
    if user.role == "admin":
        admin_session_id = os.urandom(32).hex()
        request.session['admin_session_id'] = admin_session_id
        
        # Сохраняем сессию админа в request.session
        request.session['session_storage'] = {
            admin_session_id: {
                "user_id": user.id,
                "session_id": session_id
            }
        }
    
    response = RedirectResponse(url='/account', status_code=303)
    
    # Настройка cookie в соответствии с конфигурацией
    secure = os.getenv("SECURE_COOKIES", "true").lower() == "true"
    same_site = os.getenv("SAME_SITE_POLICY", "lax")
    
    response.set_cookie(
        "csrf_token",
        os.urandom(32).hex(),
        httponly=True,
        secure=secure,
        samesite=same_site,
        max_age=int(os.getenv("SESSION_LIFETIME", 3600))
    )
    
    return response

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/', status_code=303)

