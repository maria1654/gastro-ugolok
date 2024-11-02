from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

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
        return templates.TemplateResponse("login.html", {"request": request, **session_data, "error": "Неверное имя пользователя или пароль"})
    request.session['user'] = user.username
    return RedirectResponse(url='/account', status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/', status_code=303)

