import tkinter as tk
from tkinter import simpledialog, messagebox
from database import fetch_query, execute_query
from security import check_password, hash_password

def login():
    """Форма входа"""
    root = tk.Tk()
    root.withdraw()
    
    username = simpledialog.askstring("Логин", "Введите имя пользователя:")
    password = simpledialog.askstring("Пароль", "Введите пароль:", show="*")
    
    if not username or not password:
        return None, None

    user = fetch_query("databases/users.db", "SELECT password_hash, role FROM users WHERE username = ?", (username,))
    if user and check_password(password, user[0][0]):
        return username, user[0][1]  # Возвращает имя пользователя и его роль
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль")
        return None, None

def create_admin():
    """Создание администратора при первой установке"""
    execute_query("databases/users.db", """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)
    if not fetch_query("databases/users.db", "SELECT * FROM users WHERE username = 'admin'"):
        execute_query("databases/users.db", "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')", 
                      ("admin", hash_password("admin123")))
        print(">>> Администратор создан: admin / admin123")