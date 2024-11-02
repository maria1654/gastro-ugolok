from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse
from datetime import datetime, timedelta

templates = Jinja2Templates(directory="templates")
router = APIRouter()

def get_session_data(request: Request):
    username = request.session.get('user')
    cookies_accepted = request.session.get('cookies_accepted', False)
    return {'user': username, 'cookies_accepted': cookies_accepted}

@router.get("/")
async def read_index(request: Request, session_data: dict = Depends(get_session_data)):
    return templates.TemplateResponse("index.html", {"request": request, **session_data})

@router.get("/catalog")
async def catalog(request: Request, session_data: dict = Depends(get_session_data)):
    return templates.TemplateResponse("catalog.html", {"request": request, **session_data})

@router.get("/randrecepie")
async def randrecepie(request: Request, session_data: dict = Depends(get_session_data)):
    return templates.TemplateResponse("405.html", {"request": request, **session_data})

@router.get("/account")
async def account(request: Request, session_data: dict = Depends(get_session_data)):
    if not session_data['user']:
        return RedirectResponse(url='/login', status_code=303)
    return templates.TemplateResponse("account.html", {"request": request, **session_data})

@router.get("/policy")
async def cookie_policy(request: Request, session_data: dict = Depends(get_session_data)):
    return templates.TemplateResponse("policy.html", {"request": request, **session_data})

@router.post("/accept_cookies")
async def accept_cookies(request: Request):
    response = JSONResponse({"status": "accepted"})
    expire = datetime.utcnow() + timedelta(days=365)
    response.set_cookie(
        key="cookiesAccepted",
        value="true",
        expires=expire.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
        httponly=False,
        samesite='Lax',
        path='/'
    )
    return response
