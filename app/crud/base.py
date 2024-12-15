from typing import Union, Optional, List
import mysql.connector
import logging
from app.models import UserInDB
from app.crud.initialization import get_db
from .mysql import get_recipe_mysql, save_recipe_mysql, get_all_recipes_mysql, get_last_recipe_id_mysql, get_rid_for_mysql, update_recipe_mysql, delete_recipe_mysql
from .sqlite import get_recipe_sqlite, save_recipe_sqlite, get_all_recipes_sqlite, get_last_recipe_id_sqlite, get_rid_for_sqlite, update_recipe_sqlite, delete_recipe_sqlite

logger = logging.getLogger(__name__)

def get_user(email: str) -> Optional[UserInDB]:
    conn = None
    try:
        conn = get_db()
        
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, email, hashed_password, role 
                FROM users 
                WHERE email = %s
            """, (email,))
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, hashed_password, role 
                FROM users 
                WHERE email = ?
            """, (email,))
            
        result = cursor.fetchone()
        if result:
            if isinstance(conn, mysql.connector.MySQLConnection):
                # MySQL уже возвращает словарь
                user_data = result
            else:
                # Для SQLite создаем словарь вручную
                user_data = {
                    "id": result[0],
                    "username": result[1],
                    "email": result[2],
                    "hashed_password": result[3],
                    "role": result[4]
                }
            return UserInDB(**user_data)
        return None
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def create_user(username: str, email: str, hashed_password: str) -> bool:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password, role) 
                VALUES (%s, %s, %s, %s)
            """, (username, email, hashed_password, "user"))
        else:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password, role) 
                VALUES (?, ?, ?, ?)
            """, (username, email, hashed_password, "user"))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def create_users_table() -> None:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'user'
                )
            """)
        else:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user'
                )
            """)
        conn.commit()
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def create_catalog_table() -> None:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS catalog (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    rid VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    time VARCHAR(255) NOT NULL,
                    ingredient TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    view INT DEFAULT 0,
                    `like` INT DEFAULT 0,
                    view_for_week TEXT NOT NULL
                )
            """)
        else:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rid TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    time TEXT NOT NULL,
                    ingredient TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    view INTEGER DEFAULT 0,
                    like INTEGER DEFAULT 0,
                    view_for_week TEXT NOT NULL
                )
            """)
        conn.commit()
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def get_recipe(rid: str) -> Optional[dict]:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            return get_recipe_mysql(conn, rid)
        else:
            return get_recipe_sqlite(rid)
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def save_recipe(recipe_data: dict) -> bool:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            return save_recipe_mysql(conn, recipe_data)
        else:
            return save_recipe_sqlite(recipe_data)
    except Exception as e:
        logger.error(f"Ошибка при сохранении рецепта: {str(e)}", exc_info=True)
        raise
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()


def get_all_recipes():
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            return get_all_recipes_mysql(conn)
        else:
            return get_all_recipes_sqlite(conn)
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def get_recipe_by_rid(rid: str) -> Optional[dict]:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            return get_recipe_mysql(conn, rid)
        else:
            return get_recipe_sqlite(rid)
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def get_last_recipe_id() -> Optional[int]:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            return get_last_recipe_id_mysql(conn)
        else:
            return get_last_recipe_id_sqlite(conn)
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def get_rid_for(column: str, order: str = "DESC", limit: int = 1) -> List[str]:
    """
    Получает список rid рецептов, отсортированных по указанному столбцу.

    Args:
        column (str): Столбец для сортировки. Доступные варианты:
            - "rid" - уникальный идентификатор рецепта
            - "name" - название рецепта
            - "time_for_cook" - время приготовления
            - "view" - количество просмотров
            - "like" - количество лайков
            - "view_for_week" - количество просмотров за неделю
        
        order (str): Порядок сортировки. Доступные варианты:
            - "DESC" - по убыванию (от большего к меньшему)
            - "ASC" - по возрастанию (от меньшего к большему)
            - "RAND" - случайный порядок (случайная строка)
        
        limit (int): Количество возвращаемых записей

    Returns:
        List[str]: Список rid рецептов

    Examples:
        # Получить 3 случайных рецепта
        random_rids = get_rid_for("rid", "RAND", 3)

        # Получить 5 наименее просматриваемых рецептов
        least_viewed_rids = get_rid_for("view", "ASC", 5)
    """
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            return get_rid_for_mysql(conn, column, order, limit)
        else:
            return get_rid_for_sqlite(column, order, limit)
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close() 

def create_user_data_table() -> None:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor = conn.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS user_data (
                    id INT NOT NULL,
                    first_name VARCHAR(255) NOT NULL,
                    last_name VARCHAR(255) NOT NULL,
                    birthday DATE,
                    favorite_tags TEXT,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        else:
            cursor = conn.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS user_data (
                    id INTEGER NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    birthday DATE,
                    favorite_tags TEXT,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        conn.commit()
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def create_tags_table() -> None:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor = conn.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS tags (
                    tid INT AUTO_INCREMENT PRIMARY KEY,
                    data TEXT NOT NULL
                )
            """)
        else:
            cursor = conn.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS tags (
                    tid INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL
                )
            """)
        conn.commit()
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def create_history_table() -> None:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor = conn.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS history (
                    id INT NOT NULL,
                    rid TEXT NOT NULL,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        else:
            cursor = conn.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER NOT NULL,
                    rid TEXT NOT NULL,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        conn.commit()
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def create_favorite_table() -> None:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor = conn.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS favorite (
                    id INT NOT NULL,
                    rid TEXT NOT NULL,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        else:
            cursor = conn.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS favorite (
                    id INTEGER NOT NULL,
                    rid TEXT NOT NULL,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        conn.commit()
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close() 

def create_drafts_table() -> None:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drafts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    rid VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    time VARCHAR(255) NOT NULL,
                    ingredient TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    view INT DEFAULT 0,
                    `like` INT DEFAULT 0,
                    view_for_week TEXT NOT NULL,
                    images TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        else:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    rid TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    time TEXT NOT NULL,
                    ingredient TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    view INTEGER DEFAULT 0,
                    like INTEGER DEFAULT 0,
                    view_for_week TEXT NOT NULL,
                    images TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        conn.commit()
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close()

def check_and_create_tables() -> None:
    tables = {
        'users': create_users_table,
        'catalog': create_catalog_table,
        'user_data': create_user_data_table,
        'tags': create_tags_table,
        'history': create_history_table,
        'favorite': create_favorite_table,
        'drafts': create_drafts_table
    }
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if isinstance(conn, mysql.connector.MySQLConnection):
            for table_name, create_func in tables.items():
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                if not cursor.fetchone():
                    create_func()
        else:
            for table_name, create_func in tables.items():
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not cursor.fetchone():
                    create_func()
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close() 

def save_draft_recipe(recipe_data: dict) -> bool:
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if isinstance(conn, mysql.connector.MySQLConnection):
            cursor.execute("""
                INSERT INTO drafts (
                    user_id, rid, name, time, ingredient, stage, 
                    view, `like`, view_for_week, images
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                recipe_data['user_id'],
                recipe_data['rid'],
                recipe_data['name'],
                recipe_data['time'],
                str(recipe_data['ingredient']),
                str(recipe_data['stage']),
                recipe_data.get('view', 0),
                recipe_data.get('like', 0),
                str(recipe_data.get('view_for_week', [])),
                str(recipe_data.get('images', {}))
            ))
        else:
            cursor.execute("""
                INSERT INTO drafts (
                    user_id, rid, name, time, ingredient, stage,
                    view, like, view_for_week, images
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_data['user_id'],
                recipe_data['rid'],
                recipe_data['name'],
                recipe_data['time'],
                str(recipe_data['ingredient']),
                str(recipe_data['stage']),
                recipe_data.get('view', 0),
                recipe_data.get('like', 0),
                str(recipe_data.get('view_for_week', [])),
                str(recipe_data.get('images', {}))
            ))
            
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении черновика: {str(e)}", exc_info=True)
        return False
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close() 

def update_recipe(recipe_data: dict) -> bool:
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            return update_recipe_mysql(conn, recipe_data)
        else:
            return update_recipe_sqlite(recipe_data)
    except Exception as e:
        logger.error(f"Ошибка при обновлении рецепта: {str(e)}", exc_info=True)
        return False
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close() 

def delete_recipe(rid: str) -> bool:
    """
    Удаляет рецепт по его rid.
    
    Args:
        rid (str): Уникальный идентификатор рецепта
        
    Returns:
        bool: True если рецепт успешно удален, False в противном случае
    """
    conn = None
    try:
        conn = get_db()
        if isinstance(conn, mysql.connector.MySQLConnection):
            return delete_recipe_mysql(conn, rid)
        else:
            return delete_recipe_sqlite(rid)
    finally:
        if conn and isinstance(conn, mysql.connector.MySQLConnection):
            conn.close() 