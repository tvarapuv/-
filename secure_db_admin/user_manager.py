import tkinter as tk
from tkinter import simpledialog, messagebox
from database import fetch_query, execute_query
from security import hash_password

class UserManager(tk.Toplevel):
    def __init__(self, master, db_path):
        super().__init__(master)
        self.db_path = db_path
        self.title("Управление пользователями")
        self.geometry("500x400")

        self.label = tk.Label(self, text="Список пользователей", font=("Arial", 12))
        self.label.pack(pady=10)

        self.user_listbox = tk.Listbox(self)
        self.user_listbox.pack(expand=True, fill="both", padx=10, pady=5)

        self.refresh_user_list()

        self.add_user_button = tk.Button(self, text="Добавить пользователя", command=self.add_user)
        self.add_user_button.pack(pady=5)

        self.delete_user_button = tk.Button(self, text="Удалить пользователя", command=self.delete_user)
        self.delete_user_button.pack(pady=5)

    def refresh_user_list(self):
        """Обновляет список пользователей"""
        self.user_listbox.delete(0, tk.END)
        users = fetch_query(self.db_path, "SELECT username, role FROM users")
        for user in users:
            self.user_listbox.insert(tk.END, f"{user[0]} ({user[1]})")

    def add_user(self):
        """Добавление нового пользователя"""
        username = simpledialog.askstring("Новый пользователь", "Введите имя пользователя:")
        password = simpledialog.askstring("Пароль", "Введите пароль:", show="*")
        role = simpledialog.askstring("Роль", "Введите роль (admin/user):", initialvalue="user")

        if username and password and role in ["admin", "user"]:
            hashed_password = hash_password(password)
            execute_query(self.db_path, "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                          (username, hashed_password, role))
            messagebox.showinfo("Успех", f"Пользователь {username} добавлен!")
            self.refresh_user_list()
        else:
            messagebox.showerror("Ошибка", "Некорректные данные!")

    def delete_user(self):
        """Удаление пользователя"""
        selected_index = self.user_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Ошибка", "Выберите пользователя для удаления")
            return

        selected_user = self.user_listbox.get(selected_index)
        username = selected_user.split(" (")[0]

        confirm = messagebox.askyesno("Подтверждение", f"Удалить пользователя {username}?")
        if confirm:
            execute_query(self.db_path, "DELETE FROM users WHERE username = ?", (username,))
            messagebox.showinfo("Удаление", f"Пользователь {username} удалён!")
            self.refresh_user_list()