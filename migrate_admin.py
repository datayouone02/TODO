"""
Migration script to update chat_id in tasks database when ADMIN_CHAT_ID changes.
This script updates all existing tasks to use the new ADMIN_CHAT_ID from .env file.
"""

import sqlite3
from settings import DATABASE, ADMIN_CHAT_ID

def migrate_admin_chat_id():
    """Update all tasks in the database to use the current ADMIN_CHAT_ID"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get all unique chat_ids in the database
    cursor.execute("SELECT DISTINCT chat_id FROM tasks")
    existing_chat_ids = cursor.fetchall()
    
    if not existing_chat_ids:
        print("No tasks found in database. Nothing to migrate.")
        conn.close()
        return
    
    # Update all tasks to use the new ADMIN_CHAT_ID
    cursor.execute("UPDATE tasks SET chat_id = ?", (ADMIN_CHAT_ID,))
    updated_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"✅ Migration completed successfully!")
    print(f"Updated {updated_count} task(s) to use ADMIN_CHAT_ID: {ADMIN_CHAT_ID}")
    print(f"Previous chat_id(s): {[row[0] for row in existing_chat_ids]}")

if __name__ == "__main__":
    print(f"Current ADMIN_CHAT_ID from .env: {ADMIN_CHAT_ID}")
    print("Starting migration...")
    migrate_admin_chat_id()
