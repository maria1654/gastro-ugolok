from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
from app.crud.base import get_recipe, save_recipe, get_all_recipes, get_rid_for
from app.models import Recipe
import os
import random
import string

router = APIRouter(
    prefix="/api"
)

@router.get("/recipes/{recipe_id}")
async def get_recipe_by_id(recipe_id: str) -> Dict:
    recipe = get_recipe(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    return recipe

@router.post("/recipes")
async def create_recipe(recipe: Recipe) -> JSONResponse:
    try:
        while True:
            rid = ''.join(random.choices(string.digits, k=6))
            existing_recipe = get_recipe(rid)
            if existing_recipe is None:
                break
        
        folder_path = f"recipes/{rid}"
        os.makedirs(folder_path, exist_ok=True)
        
        recipe_data = recipe.model_dump()
        recipe_data['rid'] = rid
        
        success = save_recipe(recipe_data)
        
        if not success:
            if os.path.exists(folder_path):
                os.rmdir(folder_path)
            error_msg = "Ошибка при сохранении рецепта в базу данных"
            raise HTTPException(status_code=500, detail=error_msg)
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Рецепт успешно сохранен",
                "rid": rid
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        error_msg = f"Внутренняя ошибка сервера: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg) 

@router.get("/")
async def try_api():
    return {"status": "success", "message": "True"}

@router.get("/recipes")
async def get_recipes(page: int = 1, per_page: int = 4) -> Dict:
    try:
        recipes = get_all_recipes()
        
        if not recipes:
            return {
                "recipes": [],
                "total": 0,
                "pages": 0,
                "current_page": page
            }
        
        # Вычисляем общее количество страниц
        total_recipes = len(recipes)
        total_pages = (total_recipes + per_page - 1) // per_page
        
        # Проверяем, что запрошенная страница существует
        if page > total_pages:
            page = total_pages
        
        # Получаем рецепты для текущей страницы
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_recipes = recipes[start_idx:end_idx]
        
        return {
            "recipes": page_recipes,
            "total": total_recipes,
            "pages": total_pages,
            "current_page": page
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.get("/random")
async def get_random_recipe_endpoint() -> Dict:
    try:
        random_rids = get_rid_for(column="rid", order="RAND", limit=1)
        
        if not random_rids:
            raise HTTPException(status_code=404, detail="Рецепты не найдены")
        
        random_rid = random_rids[0]
        return {"url": f"/recipe?rid={random_rid}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.get("/popular")
async def get_popular_recipes() -> Dict:
    try:
        # Получаем rid трех самых просматриваемых рецептов за неделю
        popular_rids = get_rid_for(column="view_for_week", order="DESC", limit=3)
        
        if not popular_rids:
            raise HTTPException(status_code=404, detail="Рецепты не найдены")
        
        # Получаем полную информацию о каждом рецепте
        popular_recipes = []
        for rid in popular_rids:
            recipe = get_recipe(rid)
            if recipe:
                popular_recipes.append(recipe)
        
        return {"recipes": popular_recipes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.put("/recipes/{recipe_id}")
async def update_recipe(recipe_id: str, recipe: Recipe) -> JSONResponse:
    try:
        recipe_data = recipe.model_dump()
        recipe_data['rid'] = recipe_id
        
        success = save_recipe(recipe_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Ошибка при обновлении рецепта")
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Рецепт успешно обновлен",
                "rid": recipe_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

