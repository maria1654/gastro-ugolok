from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from time import time
import random
import string
from app.crud.base import get_recipe, update_recipe, save_recipe, get_rid_for, delete_recipe
from PIL import Image
from pathlib import Path

from app.web.routers.main_router import get_session_data

router = APIRouter()

templates = Jinja2Templates(directory="templates")

session_storage = {}

@router.get("/admin/data")
async def get_admin_data(request: Request):
    if not request.session.get('admin_session_id'):
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    return {"data": "Данные администратора"}

@router.get("/admin/recipe/edit/{rid}", response_class=HTMLResponse)
async def edit_recipe(request: Request, rid: str):
    try:
        if not request.session.get('admin_session_id'):
            return RedirectResponse(url='/403', status_code=403)
            
        return templates.TemplateResponse(
            "edit_recipe.html",
            {
                "request": request,
                "rid": rid,
                "user": request.session.get("user")
            }
        )
    except AssertionError:
        return RedirectResponse(url='/403', status_code=403)

@router.post("/admin/recipe/edit/save")
async def save_edited_recipe(request: Request):
    if not request.session.get('admin_session_id'):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
        
    try:
        recipe_data = await request.json()
        
        # Получаем текущий рецепт из БД
        current_recipe = get_recipe(recipe_data.get('rid'))
        if not current_recipe:
            raise HTTPException(status_code=404, detail="Рецепт не найден")
        
        # Сохраняем данные, обновляя только редактируемые поля
        save_data = {
            'rid': recipe_data.get('rid'),
            'name': recipe_data.get('name'),
            'time': recipe_data.get('time'),
            'ingredient': recipe_data.get('ingredients', {}),
            'stage': recipe_data.get('stages', {}),
            'view': current_recipe.get('view', 0),
            'like': current_recipe.get('like', 0),
            'view_for_week': current_recipe.get('view_for_week', {})
        }
        
        success = update_recipe(save_data)  # Используем новую функцию update_recipe
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при сохранении рецепта"
            )
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Рецепт успешно обновлен",
                "rid": save_data['rid']
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при сохранении рецепта: {str(e)}"
        )

@router.post("/admin/recipe/upload-image")
async def upload_recipe_image(request: Request, image: UploadFile = File(...)):
    if not request.session.get('admin_session_id'):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        form = await request.form()
        rid = form.get('rid')
        print(f"Получен rid: {rid}")
        
        # Используем путь в соответствии с настройками static_paths
        recipe_dir = Path(f"static/recipesbase/{rid}")
        print(f"Создаем директорию: {recipe_dir}")
        recipe_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = recipe_dir / "title.jpg"
        print(f"Путь для сохранения: {image_path}")
        
        image_content = await image.read()
        with open(image_path, "wb") as f:
            f.write(image_content)
        print(f"Файл сохранен")
        
        # Оптимизируем изображение
        with Image.open(image_path) as img:
            max_size = (800, 800)
            img.thumbnail(max_size, Image.LANCZOS)
            img.save(image_path, "JPEG", quality=85, optimize=True)
        print(f"Изображение оптимизировано")
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Изображение успешно загружено"
            }
        )
        
    except Exception as e:
        print(f"Ошибка при загрузке изображения: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при загрузке изображения: {str(e)}"
        )

@router.get("/admin/recipe/edit/{rid}", response_class=HTMLResponse)
async def edit_recipe(request: Request, rid: str, session_data: dict = Depends(get_session_data)):
    if not session_data['isUserLoggedIn']:
        return RedirectResponse(url='/login', status_code=303)
    
    return templates.TemplateResponse(
        "edit_recipe.html",
        {
            "request": request, 
            "rid": rid, 
            "timestamp": int(time() * 1000),
            **session_data
        }
    )

@router.get("/admin/recipe/new", response_class=HTMLResponse)
async def new_recipe(request: Request, session_data: dict = Depends(get_session_data)):
    if not session_data['isUserLoggedIn']:
        return RedirectResponse(url='/login', status_code=303)
    
    return templates.TemplateResponse(
        "edit_recipe.html",
        {
            "request": request,
            "rid": "new",
            "timestamp": int(time() * 1000),
            "is_new": True,
            **session_data
        }
    )

@router.get("/admin/recipe/create", response_class=HTMLResponse)
async def create_recipe_page(request: Request, session_data: dict = Depends(get_session_data)):
    if not session_data['isUserLoggedIn']:
        return RedirectResponse(url='/login', status_code=303)
    
    return templates.TemplateResponse(
        "edit_recipe.html",
        {
            "request": request,
            "rid": "new",
            "timestamp": int(time() * 1000),
            "is_new": True,
            **session_data
        }
    )

@router.post("/admin/recipe/create")
async def create_recipe(request: Request):
    if not request.session.get('admin_session_id'):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
        
    try:
        recipe_data = await request.json()
        
        while True:
            rid = ''.join(random.choices(string.digits, k=6))
            existing_recipe = get_recipe(rid)
            if existing_recipe is None:
                break
        
        save_data = {
            'rid': rid,
            'name': recipe_data.get('name'),
            'time': recipe_data.get('time'),
            'ingredient': recipe_data.get('ingredients', {}),
            'stage': recipe_data.get('stages', {}),
            'view': 0,
            'like': 0,
            'view_for_week': {}
        }
        
        success = save_recipe(save_data)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при сохранении рецепта"
            )
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Рецепт успешно создан",
                "rid": rid
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании рецепта: {str(e)}"
        )

@router.delete("/admin/recipe/{rid}")
async def delete_recipe_route(request: Request, rid: str):
    if not request.session.get('admin_session_id'):
        raise HTTPException(status_code=403, detail="Доступ запрещен")
        
    try:
        success = delete_recipe(rid)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Рецепт не найден или не может быть удален"
            )
        
        # Также удаляем файлы изображений рецепта
        recipe_dir = Path(f"static/recipesbase/{rid}")
        if recipe_dir.exists():
            for file in recipe_dir.glob('*'):
                file.unlink()
            recipe_dir.rmdir()
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Рецепт успешно удален"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении рецепта: {str(e)}"
        )