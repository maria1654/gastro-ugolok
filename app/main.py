from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
import os

from app.routers import main_router, auth_router
from app.database import create_users_table

load_dotenv()

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),
    session_cookie="session_id"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(main_router.router)
app.include_router(auth_router.router)

templates = Jinja2Templates(directory="templates")

# Обработчики исключений

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(405)
async def method_not_allowed(request: Request, exc):
    return templates.TemplateResponse("405.html", {"request": request}, status_code=405)

@app.on_event("startup")
def startup_event():
    create_users_table()
