import math
import pandas as pd

from sqlalchemy import select
from core.db import SessionLocal
from models.indicator import IndicatorDB
from state.memory import candles, indicator_values


def clean(values):
    return [
        None if (v is None or not math.isfinite(v)) else float(v)
        for v in values
    ]


def calc_sma(series, period):
    return series.rolling(period).mean().tolist()


def calc_ema(series, period):
    return series.ewm(span=period, adjust=False).mean().tolist()


async def recalc_indicator(ind: IndicatorDB):
    if not candles:
        return

    df = pd.DataFrame(candles)
    close = df["close"]

    if ind.name == "sma":
        values = calc_sma(close, ind.period)
    elif ind.name == "ema":
        values = calc_ema(close, ind.period)
    else:
        values = []

    indicator_values[ind.id] = values


async def recalc_all_indicators():
    async with SessionLocal() as session:
        result = await session.execute(select(IndicatorDB))
        inds = result.scalars().all()

    for ind in inds:
        await recalc_indicator(ind)
