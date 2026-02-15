import httpx
import pandas as pd

from core.config import BYBIT_URL
from state.memory import candles
from services.indicators import recalc_all_indicators


async def fetch_candles():
    params = {
        "category": "linear",
        "symbol": "BTCUSDT",
        "interval": "1",
        "limit": 100
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(BYBIT_URL, params=params)
        data = r.json()

    raw = data["result"]["list"]

    df = pd.DataFrame(raw, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "turnover"
    ])

    df = df.astype(float).sort_values("timestamp")
    candles.clear()
    candles.extend(df.to_dict(orient="records"))

    await recalc_all_indicators()
