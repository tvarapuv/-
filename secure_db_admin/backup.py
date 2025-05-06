import shutil
import os
from datetime import datetime
from security import encrypt, KEY

BACKUP_DIR = "backups/"

def backup_db():
    """Создание резервной копии БД"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    backup_filename = os.path.join(BACKUP_DIR, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    with open("db/database_encrypted.db", "rb") as f:
        encrypted_data = f.read()
    
    with open(backup_filename, "wb") as f:
        f.write(encrypt(encrypted_data, KEY))
    
    return backup_filename