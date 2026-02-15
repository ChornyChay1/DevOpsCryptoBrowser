import asyncio
from fastapi import FastAPI

from core.db import engine, Base
from api.indicator_routes import router as indicator_router
from services.candles import fetch_candles

app = FastAPI()
app.include_router(indicator_router)


async def candle_loop():
    while True:
        try:
            await fetch_candles()
        except Exception as e:
            print("fetch error", e)

        await asyncio.sleep(10)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    asyncio.create_task(candle_loop())
