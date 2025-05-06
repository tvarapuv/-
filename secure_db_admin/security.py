import bcrypt

def hash_password(password):
    """Хеширование пароля"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed_password):
    """Проверка пароля"""
    return bcrypt.checkpw(password.encode(), hashed_password)