import os

from dotenv import load_dotenv

load_dotenv()


def getDatabaseUrl():
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@postgres:5432/{db}"
    return DATABASE_URL


def get_bybit_url():
    return "https://api.bybit.com/v5/market/kline"


def get_app_name():
    return os.getenv("APP_NAME")


def get_environment():
    return os.getenv("ENVIRONMENT")


def get_debug():
    return os.getenv("DEBUG")