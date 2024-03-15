import os

from dotenv import load_dotenv

# Загружаем скрытые данные из файла .env

load_dotenv()

PROJECT_DEBUG = os.environ.get("PROJECT_DEBUG")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
# DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
# DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
# DB_USER_TEST = os.environ.get("DB_USER_TEST")
# DB_PASS_TEST = os.environ.get("DB_PASS_TEST")

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

SECRET_AUTH = os.environ.get("SECRET_AUTH")
#
# SENTRY_URL = os.environ.get("SENTRY_URL")
#
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")

DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
PRODUCE_TOPIC = os.environ.get("PRODUCE_TOPIC")
