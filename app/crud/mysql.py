from typing import Optional, List
import mysql.connector
from app.models import UserInDB
import json
import logging

logger = logging.getLogger(__name__)

def get_user_mysql(conn: mysql.connector.MySQLConnection, email: str) -> Optional[UserInDB]:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    return UserInDB(**row) if row else None

def create_user_mysql(
    conn: mysql.connector.MySQLConnection,
    username: str,
    email: str,
    hashed_password: str
) -> bool:
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False 

def create_catalog_table_mysql(conn: mysql.connector.MySQLConnection) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catalog (
            rid CHAR(6) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            time_for_cook VARCHAR(100) NOT NULL,
            ingredient JSON NOT NULL,
            stage JSON NOT NULL,
            view INT DEFAULT 0,
            `like` INT DEFAULT 0,
            view_for_week JSON NOT NULL
        )
    """)
    conn.commit() 

def get_recipe_mysql(conn: mysql.connector.MySQLConnection, rid: str) -> Optional[dict]:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM catalog WHERE rid = %s", (rid,))
    row = cursor.fetchone()
    
    if row:
        # Преобразуем JSON строки в словари Python
        row['ingredient'] = json.loads(row['ingredient'])
        row['stage'] = json.loads(row['stage'])
        row['view_for_week'] = json.loads(row['view_for_week'])
        return row
    return None 

def save_recipe_mysql(conn, recipe_data: dict) -> bool:
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO catalog (
                rid, name, time, ingredient, stage, 
                view, `like`, view_for_week
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            recipe_data['rid'],
            recipe_data['name'],
            recipe_data['time'],
            json.dumps(recipe_data['ingredient']),
            json.dumps(recipe_data['stage']),
            recipe_data['view'],
            recipe_data['like'],
            json.dumps(recipe_data['view_for_week'])
        ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e 

def get_all_recipes_mysql(conn: mysql.connector.MySQLConnection) -> List[dict]:
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM catalog")
        rows = cursor.fetchall()
        
        recipes = []
        for row in rows:
            row['ingredient'] = json.loads(row['ingredient'])
            row['stage'] = json.loads(row['stage'])
            row['view_for_week'] = json.loads(row['view_for_week'])
            recipes.append(row)
        
        return recipes
    except Exception as e:
        logger.error(f"Ошибка при получении всех рецептов из MySQL: {str(e)}")
        return []

def get_last_recipe_id_mysql(conn: mysql.connector.MySQLConnection) -> Optional[int]:
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM catalog")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except Exception as e:
        logger.error(f"Ошибка при получении последнего ID из MySQL: {str(e)}")
        return None

def get_rid_for_mysql(conn: mysql.connector.MySQLConnection, 
                     column: str, 
                     order: str = "DESC", 
                     limit: int = 1) -> List[str]:
    try:
        cursor = conn.cursor()
        order = order.upper()
        
        # Проверяем правильность параметра order
        if order not in ["ASC", "DESC", "RAND"]:
            raise ValueError("Параметр order должен быть 'ASC', 'DESC' или 'RAND'")
            
        # Для случайной сортировки используем RAND()
        if order == "RAND":
            cursor.execute("""
                SELECT rid 
                FROM catalog 
                ORDER BY RAND()
                LIMIT %s
            """, (limit,))
        else:
            cursor.execute(f"""
                SELECT rid 
                FROM catalog 
                ORDER BY `{column}` {order}
                LIMIT %s
            """, (limit,))
        
        results = cursor.fetchall()
        return [row[0] for row in results]
    except Exception as e:
        logger.error(f"Ошибка при получении rid из MySQL: {str(e)}")
        return []

def update_recipe_mysql(conn: mysql.connector.MySQLConnection, recipe_data: dict) -> bool:
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE catalog 
            SET name = %s, 
                time = %s, 
                ingredient = %s, 
                stage = %s,
                view = %s,
                `like` = %s,
                view_for_week = %s
            WHERE rid = %s
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
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка при обновлении рецепта: {e}")
        return False

def delete_recipe_mysql(conn: mysql.connector.MySQLConnection, rid: str) -> bool:
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM catalog WHERE rid = %s", (rid,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Ошибка при удалении рецепта из MySQL: {str(e)}")
        return False