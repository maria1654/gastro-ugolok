import os
import sqlite3
from typing import Union
from urllib.parse import urlparse
import mysql.connector
from dotenv import load_dotenv

DBConnection = Union[mysql.connector.MySQLConnection, sqlite3.Connection]

class DatabaseConnection:
    @staticmethod
    def get_db() -> DBConnection:
        load_dotenv()
        db_url = os.getenv('DATABASE_URL')
        
        try:
            if db_url:
                parsed = urlparse(db_url)
                return mysql.connector.connect(
                    host=parsed.hostname,
                    user=parsed.username,
                    password=parsed.password,
                    database=parsed.path.lstrip('/'),
                    autocommit=True,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci'
                )
            raise Exception("No DATABASE_URL")
        except Exception as e:
            return sqlite3.connect('app_local.db', 
                                 detect_types=sqlite3.PARSE_DECLTYPES,
                                 isolation_level=None)

get_db = DatabaseConnection.get_db
