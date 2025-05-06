import sqlite3
import os
import shutil
from datetime import datetime

# Папки для баз данных и резервных копий
DB_FOLDER = "databases"
BACKUP_FOLDER = "backups"

# Создание папок, если их нет
for folder in [DB_FOLDER, BACKUP_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def create_new_db(db_name):
    """Создаёт новую базу данных с таблицами 'records' и 'logs'."""
    db_path = os.path.join(DB_FOLDER, f"{db_name}.db")
    
    if os.path.exists(db_path):
        return "База данных уже существует!"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Таблица для хранения данных
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Таблица логов действий пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            user TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    return f"База данных '{db_name}' успешно создана!"

def execute_query(db_path, query, params=()):
    """Выполняет SQL-запрос (INSERT, UPDATE, DELETE)"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
    finally:
        conn.close()

def fetch_query(db_path, query, params=()):
    """Выполняет SQL-запрос (SELECT) и возвращает результат"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        return []
    finally:
        conn.close()

def log_action(db_path, action, user):
    """Записывает действие пользователя в журнал"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query(db_path, "INSERT INTO logs (action, user, timestamp) VALUES (?, ?, ?)", (action, user, timestamp))

def backup_database(db_path):
    """Создаёт резервную копию базы данных"""
    if not os.path.exists(db_path):
        return "Ошибка: База данных не найдена."

    db_name = os.path.basename(db_path)
    backup_path = os.path.join(BACKUP_FOLDER, f"backup_{db_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    
    try:
        shutil.copy(db_path, backup_path)
        return f"Резервная копия сохранена: {backup_path}"
    except Exception as e:
        return f"Ошибка при резервном копировании: {e}"

def restore_database(db_path, backup_file):
    """Восстанавливает базу данных из резервной копии"""
    if not os.path.exists(backup_file):
        return "Ошибка: Файл резервной копии не найден."

    try:
        shutil.copy(backup_file, db_path)
        return "База данных успешно восстановлена!"
    except Exception as e:
        return f"Ошибка при восстановлении: {e}"