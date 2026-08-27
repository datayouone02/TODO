import sqlite3
from settings import DATABASE

user_data = {}

def get_db_connection():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    return conn

def create_tasks_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                chat_id INTEGER,
                product_link TEXT,
                buyer_name TEXT,
                tags TEXT,
                additional_info TEXT,
                expiration_date DATE
            )
        ''')
        conn.commit()

create_tasks_table()