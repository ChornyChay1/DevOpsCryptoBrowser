import os
from dotenv import load_dotenv

load_dotenv()

def getDatabaseUrl():
    return os.getenv("DATABASE_URL")

BYBIT_URL = "https://api.bybit.com/v5/market/kline"

APP_NAME = os.getenv("APP_NAME")
ENVIRONMENT = os.getenv("APP_NAME")
DEBUG = os.getenv("DEBUG")
CORS_ORIGINS = os.getenv("CORS_ORIGINS")
API_PREFIX = os.getenv("API_PREFIX")