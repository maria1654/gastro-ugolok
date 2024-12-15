import sqlite3
from app.models import UserInDB
from app.crud.initialization import get_db
from typing import Optional, List
import json
import logging

logger = logging.getLogger(__name__)

def get_user_sqlite(email: str) -> Optional[UserInDB]:
    conn = None
    try:
        conn = get_db()
        if not isinstance(conn, sqlite3.Connection):
            raise ValueError("Expected SQLite connection")
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            user_dict = dict(zip(columns, row))
            return UserInDB(**user_dict)
        return None
    finally:
        if conn:
            conn.close()

def create_user_sqlite(username: str, email: str, hashed_password: str) -> bool:
    conn = None
    try:
        conn = get_db()
        if not isinstance(conn, sqlite3.Connection):
            raise ValueError("Expected SQLite connection")
            
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        if conn:
            conn.close() 

def create_catalog_table_sqlite(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catalog (
            rid CHAR(6) PRIMARY KEY,
            name TEXT NOT NULL,
            time_for_cook TEXT NOT NULL,
            ingredient TEXT NOT NULL,
            stage TEXT NOT NULL,
            view INTEGER DEFAULT 0,
            "like" INTEGER DEFAULT 0,
            view_for_week TEXT NOT NULL
        )
    """)
    conn.commit() 

def get_recipe_sqlite(rid: str) -> Optional[dict]:
    conn = None
    try:
        conn = get_db()
        if not isinstance(conn, sqlite3.Connection):
            raise ValueError("Expected SQLite connection")
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM catalog WHERE rid = ?", (rid,))
        row = cursor.fetchone()
        
        if row:
            columns = [col[0] for col in cursor.description]
            recipe_dict = dict(zip(columns, row))
            recipe_dict['ingredient'] = json.loads(recipe_dict['ingredient'], strict=False)
            recipe_dict['stage'] = json.loads(recipe_dict['stage'], strict=False)
            recipe_dict['view_for_week'] = json.loads(recipe_dict['view_for_week'], strict=False)
            return recipe_dict
        return None
    finally:
        if conn:
            conn.close() 

def save_recipe_sqlite(recipe_data: dict) -> bool:
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO catalog (
                rid, name, time, ingredient, stage, 
                view, "like", view_for_week
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            recipe_data['rid'],
            recipe_data['name'],
            recipe_data['time'],
            json.dumps(recipe_data['ingredient'], ensure_ascii=False),
            json.dumps(recipe_data['stage'], ensure_ascii=False),
            recipe_data['view'],
            recipe_data['like'],
            json.dumps(recipe_data['view_for_week'], ensure_ascii=False)
        ))
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        raise e

def get_all_recipes_sqlite(conn: sqlite3.Connection) -> List[dict]:
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM catalog")
        rows = cursor.fetchall()
        
        recipes = []
        for row in rows:
            columns = [col[0] for col in cursor.description]
            recipe_dict = dict(zip(columns, row))
            recipe_dict['ingredient'] = json.loads(recipe_dict['ingredient'], strict=False)
            recipe_dict['stage'] = json.loads(recipe_dict['stage'], strict=False)
            recipe_dict['view_for_week'] = json.loads(recipe_dict['view_for_week'], strict=False)
            recipes.append(recipe_dict)
        
        return recipes
    except Exception as e:
        logger.error(f"Ошибка при получении всех рецептов из SQLite: {str(e)}")
        return []

def get_last_recipe_id_sqlite(conn: sqlite3.Connection) -> Optional[int]:
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM catalog")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except Exception as e:
        logger.error(f"Ошибка при получении последнего ID из SQLite: {str(e)}")
        return None

def get_rid_for_sqlite(column: str, order: str = "DESC", limit: int = 1) -> List[str]:
    conn = None
    try:
        conn = get_db()
        if not isinstance(conn, sqlite3.Connection):
            raise ValueError("Expected SQLite connection")
            
        cursor = conn.cursor()
        order = order.upper()
        
        # Проверяем правильность параметра order
        if order not in ["ASC", "DESC", "RAND"]:
            raise ValueError("Параметр order должен быть 'ASC', 'DESC' или 'RAND'")
            
        # Для случайной сортировки используем RANDOM()
        if order == "RAND":
            cursor.execute("""
                SELECT rid 
                FROM catalog 
                ORDER BY RANDOM()
                LIMIT ?
            """, (limit,))
        else:
            cursor.execute(f"""
                SELECT rid 
                FROM catalog 
                ORDER BY {column} {order}
                LIMIT ?
            """, (limit,))
        
        results = cursor.fetchall()
        return [row[0] for row in results]
    except Exception as e:
        logger.error(f"Ошибка при получении rid из SQLite: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def update_recipe_sqlite(recipe_data: dict) -> bool:
    try:
        connection = get_db()
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE catalog 
            SET name = ?, 
                time = ?, 
                ingredient = ?, 
                stage = ?,
                view = ?,
                like = ?,
                view_for_week = ?
            WHERE rid = ?
        """, (
            recipe_data['name'],
            recipe_data['time'],
            json.dumps(recipe_data['ingredient'], ensure_ascii=False),
            json.dumps(recipe_data['stage'], ensure_ascii=False),
            recipe_data['view'],
            recipe_data['like'],
            json.dumps(recipe_data['view_for_week'], ensure_ascii=False),
            recipe_data['rid']
        ))
            
        connection.commit()
        return True
    except Exception as e:
        print(f"Ошибка при обновлении рецепта: {e}")
        return False
    finally:
        if connection:
            connection.close()

def delete_recipe_sqlite(rid: str) -> bool:
    conn = None
    try:
        conn = get_db()
        if not isinstance(conn, sqlite3.Connection):
            raise ValueError("Expected SQLite connection")
            
        cursor = conn.cursor()
        cursor.execute("DELETE FROM catalog WHERE rid = ?", (rid,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Ошибка при удалении рецепта из SQLite: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()