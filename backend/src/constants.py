import os

# Определяем текущую директорию скрипта
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Переходим на уровень выше
PARENT_DIR = os.path.dirname(BASE_DIR)

# Теперь создаем путь к папке images, которая находится на уровне выше
IMAGES_DIR = os.path.join(PARENT_DIR, "images")
