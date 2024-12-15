from fastapi import FastAPI, Request, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.web.routers import main_router, auth_router, admin_router
from app.crud.base import check_and_create_tables
from app.api.routers import db_routers
from app.web.middleware import setup_middleware

load_dotenv()

app = FastAPI()

setup_middleware(app)

static_paths = {
    "styles": "css",
    "js": "js",
    "fonts": "fonts", 
    "images": "images",
    "recipes": "recipesbase"
}
for path, directory in static_paths.items():
    app.mount(f"/{path}", StaticFiles(directory=f"static/{directory}"), name=path)

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/403")
async def forbidden_page(request: Request):
    return templates.TemplateResponse(
        "403.html",
        {"request": request},
        status_code=403
    )

app.include_router(router)

app.include_router(main_router.router)
app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(db_routers.router)

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(405)
async def method_not_allowed(request: Request, exc):
    if request.url.path.startswith('/api'):
        return JSONResponse(
            status_code=405,
            content={"detail": "Метод не разрешен"}
        )
    return templates.TemplateResponse("405.html", {"request": request}, status_code=405)

@app.on_event("startup")
async def startup_event():
    check_and_create_tables()