import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BYBIT_URL = "https://api.bybit.com/v5/market/kline"
