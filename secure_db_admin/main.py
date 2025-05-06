import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import os
from datetime import datetime
from database import create_new_db, fetch_query, execute_query, log_action
from auth import login, create_admin
from user_manager import UserManager

class DatabaseManager(tk.Tk):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.db_path = None

        self.title(f"Управление базами данных - Вошёл: {username} ({role})")
        self.geometry("500x400")

        tk.Label(self, text=f"Вы вошли как: {username} ({role})", font=("Arial", 12)).pack(pady=5)

        tk.Button(self, text="Выбрать базу данных", command=self.select_database).pack(pady=5)
        tk.Button(self, text="Создать новую базу", command=self.create_database).pack(pady=5)

        if self.role == "admin":
            tk.Button(self, text="Удалить базу данных", command=self.delete_database).pack(pady=5)
            tk.Button(self, text="Журнал действий", command=self.view_logs).pack(pady=5)
            tk.Button(self, text="Управление пользователями", command=self.manage_users).pack(pady=5)

        tk.Button(self, text="Выход", command=self.quit).pack(pady=10)

    def view_logs(self):

        if self.role != "admin":
            messagebox.showerror("Ошибка", "Только админ может просматривать журнал действий")
            return

        if not self.db_path:
            messagebox.showerror("Ошибка", "Сначала выберите базу данных")
            return
    
        logs = fetch_query(self.db_path, "SELECT action, user, timestamp FROM logs")
        log_window = tk.Toplevel(self)
        log_window.title("Журнал действий")
        log_window.geometry("600x400")

        tk.Label(log_window, text="Журнал действий", font=("Arial", 12)).pack(pady=10)

        log_listbox = tk.Listbox(log_window)
        log_listbox.pack(expand=True, fill="both", padx=10, pady=5)

        for log in logs:
            log_listbox.insert(tk.END, f"{log[2]} | {log[1]}: {log[0]}")

    def manage_users(self):
        if self.role != "admin":
            messagebox.showerror("Ошибка", "Только админ может управлять пользователями")
            return

        from user_manager import UserManager  # ✅ Импорт внутри метода, чтобы избежать циклических импортов
        UserManager(self, "databases/users.db")
    
    def select_database(self):
        """Выбор базы данных и открытие редактора"""
        self.db_path = filedialog.askopenfilename(initialdir="databases", title="Выберите базу данных",
                                                  filetypes=[("SQLite файлы", "*.db")])
        if self.db_path:
            messagebox.showinfo("Выбрана база данных", f"Подключено к {self.db_path}")
            self.update_existing_tables()
            DataEditor(self, self.db_path, self.username, self.role)

    def update_existing_tables(self):
        """✅ Добавляет недостающие столбцы в старые базы"""
        existing_columns = fetch_query(self.db_path, "PRAGMA table_info(records)")
        existing_column_names = [col[1] for col in existing_columns]

        if "modified_by" not in existing_column_names:
            execute_query(self.db_path, "ALTER TABLE records ADD COLUMN modified_by TEXT DEFAULT '-'")
        if "last_modified" not in existing_column_names:
            execute_query(self.db_path, "ALTER TABLE records ADD COLUMN last_modified TEXT DEFAULT '-'")

    def create_database(self):
        """Создание новой базы"""
        db_name = simpledialog.askstring("Создать БД", "Введите имя базы данных:")
        if db_name:
            result = create_new_db(db_name)
            messagebox.showinfo("Результат", result)

    def delete_database(self):
        """Удаление базы данных (только админ)"""
        if self.role != "admin":
            messagebox.showerror("Ошибка", "Только админ может удалять базы данных")
            return

        if not self.db_path:
            messagebox.showerror("Ошибка", "Сначала выберите базу данных")
            return

        confirm = messagebox.askyesno("Подтверждение", f"Удалить базу {self.db_path}?")
        if confirm:
            os.remove(self.db_path)
            messagebox.showinfo("Удаление", "База данных удалена!")

class DataEditor(tk.Toplevel):
    """Окно редактирования данных таблицы"""

    def __init__(self, master, db_path, username, role):
        super().__init__(master)
        self.master = master  # Сохраняем ссылку на главное окно
        self.db_path = db_path
        self.username = username
        self.role = role

        self.title(f"Редактирование базы данных - {os.path.basename(db_path)}")
        self.geometry("1000x500")

        self.tree = ttk.Treeview(self)
        self.tree.pack(expand=True, fill="both")

        self.load_data()

        # ✅ Кнопки управления записями
        self.add_button = tk.Button(self, text="Добавить запись", command=self.add_record)
        self.add_button.pack(pady=5)

        self.edit_button = tk.Button(self, text="Редактировать запись", command=self.edit_record)
        self.edit_button.pack(pady=5)

        self.delete_button = tk.Button(self, text="Удалить запись", command=self.delete_record)
        self.delete_button.pack(pady=5)

        # ✅ Кнопка "Назад" для возврата в главное меню
        self.back_button = tk.Button(self, text="Назад", command=self.go_back)
        self.back_button.pack(pady=10)

    def go_back(self):
        """✅ Закрывает редактор и возвращает в главное меню"""
        self.destroy()
        self.master.deiconify()  # Показываем главное окно снова

    def load_data(self):
        """✅ Загружает данные из таблицы records"""
        data = fetch_query(self.db_path, "SELECT * FROM records")

        self.tree["columns"] = ("ID", "Название", "Значение", "Создано пользователем", "Дата создания", "Кем изменено", "Дата изменения")
        self.tree.heading("#0", text="", anchor="w")
        self.tree.column("#0", width=0, stretch=tk.NO)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in data:
            self.tree.insert("", "end", values=row)

    def add_record(self):
        """✅ Добавление новой записи"""
        name = simpledialog.askstring("Добавить запись", "Введите название:")
        value = simpledialog.askstring("Добавить запись", "Введите значение:")

        if name and value:
            execute_query(self.db_path, 
                          "INSERT INTO records (name, value, created_by, created_at, modified_by, last_modified) VALUES (?, ?, ?, ?, ?, ?)",
                          (name, value, self.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-", "-"))
            log_action(self.db_path, f"Добавил запись: {name}", self.username)
            self.load_data()

    def edit_record(self):
        """✅ Редактирование существующей записи"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите запись для редактирования")
            return

        record = self.tree.item(selected_item)["values"]
        old_name, old_value = record[1], record[2]

        new_name = simpledialog.askstring("Редактирование", f"Введите новое название для '{old_name}':", initialvalue=old_name)
        new_value = simpledialog.askstring("Редактирование", f"Введите новое значение для '{old_name}':", initialvalue=old_value)

        changes = []
        if new_name and new_name != old_name:
            changes.append(f"Название: {old_name} → {new_name}")
        if new_value and new_value != old_value:
            changes.append(f"Значение: {old_value} → {new_value}")

        if changes:
            execute_query(self.db_path, 
                          "UPDATE records SET name = ?, value = ?, modified_by = ?, last_modified = ? WHERE id = ?", 
                          (new_name, new_value, self.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record[0]))
            log_action(self.db_path, f"Изменение: {', '.join(changes)}", self.username)
            self.load_data()

    def delete_record(self):
        """✅ Удаление записи"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите запись для удаления")
            return

        record = self.tree.item(selected_item)["values"]
        confirm = messagebox.askyesno("Подтверждение", f"Удалить запись '{record[1]}'?")
        if confirm:
            execute_query(self.db_path, "DELETE FROM records WHERE id = ?", (record[0],))
            log_action(self.db_path, f"Удалил запись '{record[1]}'", self.username)
            self.load_data()
if __name__ == "__main__":
    create_admin()
    user, role = login()
    if user:
        app = DatabaseManager(user, role)
        app.mainloop()


            