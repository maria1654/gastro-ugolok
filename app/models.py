from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12
)

class User(BaseModel):
    username: str

class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    role: str = "user"
    
    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)

class Recipe(BaseModel):
    name: str
    time: str
    ingredient: Dict[str, Dict[str, str]]
    stage: Dict[str, Dict[str, str]]
    view: int = 0
    like: int = 0
    view_for_week: List = []
    images: Optional[Dict[str, Any]] = {}
    user_id: Optional[int] = None
