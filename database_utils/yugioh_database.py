import sqlite3
from database_utils import yugioh_queries
def connection():
    try:
        conn = sqlite3.connect('database_utils/database.db')
        cursor = conn.cursor()
        cursor.execute(yugioh_queries.TABLE_INIT_)
        return conn
    except Exception as Error:
        print(Error)

def close_connection():
    try:
        conn = sqlite3.close()
        return conn
    except Exception as Error:
        print(Error)
