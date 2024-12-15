from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse
from datetime import datetime, timedelta
import httpx
import logging
import os

templates = Jinja2Templates(directory="templates")
router = APIRouter()

def get_session_data(request: Request):
    username = request.session.get('user')
    cookies_accepted = request.session.get('cookies_accepted', False)
    return {
        'user': username, 
        'cookies_accepted': cookies_accepted,
        'isUserLoggedIn': username is not None,
        'currentPage': request.url.path
    }

@router.get("/")
async def read_index(request: Request, session_data: dict = Depends(get_session_data)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost/api/popular")
            data = response.json()
            popular_recipes = data.get("recipes", [])
    except Exception as e:
        logging.error(f"Ошибка при получении популярных рецептов: {str(e)}")
        popular_recipes = []
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            **session_data,
            "popular_recipes": popular_recipes
        }
    )

@router.get("/catalog")
async def catalog(request: Request, page: int = 1, session_data: dict = Depends(get_session_data)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost/api/recipes?page={page}")
            data = response.json()
        
        if not isinstance(data, dict) or "recipes" not in data:
            raise ValueError("Некорректная структура данных от API")
        
        recipes = data.get("recipes", [])
        total = data.get("total", len(recipes))
        pages = data.get("pages", 1)
        current_page = data.get("current_page", page)
        
    except Exception as e:
        logging.error(f"Ошибка при получении данных из API: {str(e)}")
        
        # Используем тестовые данные в случае ошибки
        recipes = []
        total = len(recipes)
        pages = 1
        current_page = 1
    
    return templates.TemplateResponse(
        "catalog.html", 
        {
            "request": request, 
            **session_data,
            "recipes": recipes,
            "total_recipes": total,
            "total_pages": pages,
            "current_page": current_page
        }
    )

@router.get("/itsfine")
async def randrecepie(request: Request, session_data: dict = Depends(get_session_data)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost/api/random")
            data = response.json()
            
        url = data["url"]
        rid = url.split("=")[-1]
            
        return RedirectResponse(
            url=f"/recipe?rid={rid}",
            status_code=303
        )
            
    except Exception as e:
        logging.error(f"Ошибка при получении случайного рецепта: {str(e)}")
        return templates.TemplateResponse("405.html", {"request": request, **session_data})

@router.get("/account")
async def account(request: Request, session_data: dict = Depends(get_session_data)):
    if not request.session.get('user'):
        return RedirectResponse(url='/login', status_code=303)
    return templates.TemplateResponse("account.html", {
        "request": request, 
        "user": request.session.get('user'),
        "session": request.session,
        **session_data
    })

@router.get("/policy")
async def cookie_policy(request: Request, session_data: dict = Depends(get_session_data)):
    return templates.TemplateResponse("policy.html", {"request": request, **session_data})

@router.post("/accept_cookies")
async def accept_cookies(request: Request):
    response = JSONResponse({"status": "accepted"})
    expire = datetime.now() + timedelta(days=365)
    response.set_cookie(
        key="cookiesAccepted",
        value="true",
        expires=expire.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
        httponly=False,
        samesite='Lax',
        path='/'
    )
    return response

@router.get("/recipe")
async def recipe(request: Request, rid: str, session_data: dict = Depends(get_session_data)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost/api/recipes/{rid}")
            recipe = response.json()
        
        if not recipe:
            raise ValueError("Рецепт не найден")
        
        recipe['images'] = {}
        for step_key in recipe['stage'].keys():
            recipe['images'][step_key] = []
            for i in range(1, 16):
                image_path = f"static/recipesbase/{recipe['rid']}/{step_key}_{i}.jpg"
                if os.path.exists(image_path):
                    recipe['images'][step_key].append(f"{step_key}_{i}.jpg")
        
    except Exception as e:
        logging.error(f"Ошибка при получении данных рецепта из API: {str(e)}")
        return templates.TemplateResponse("404.html", {"request": request, **session_data}, status_code=404)
    
    return templates.TemplateResponse(
        "recipe.html", 
        {
            "request": request, 
            **session_data,
            "recipe": recipe
        }
    )
