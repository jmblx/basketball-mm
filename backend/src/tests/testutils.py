import time
import uuid


def generate_unique_email():
    unique_string = str(uuid.uuid4())  # Генерируем уникальный UUID
    timestamp = int(time.time())  # Получаем текущую временную метку
    email = f"user_{unique_string}_{timestamp}@example.com"  # Формируем электронную почту
    return email
