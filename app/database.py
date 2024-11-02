import sqlite3
from app.models import UserInDB
from db import get_db, create_users_table

def get_user(email: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return UserInDB(username=row["username"], email=row["email"], hashed_password=row["hashed_password"])
    return None

def create_user_in_db(username: str, email: str, hashed_password: str):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
