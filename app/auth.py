from passlib.context import CryptContext
from dotenv import load_dotenv

from app.crud.base import get_user, create_user as create_user_in_db

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(username: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    return create_user_in_db(username, email, hashed_password)
