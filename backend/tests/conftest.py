import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from state import memory

test_app = FastAPI()
test_app.include_router(router)

@pytest.fixture
def client():
    with TestClient(test_app) as c:
        yield c


@pytest.fixture
def sample_series():
    return pd.Series([10, 12, 11, 13, 15, 14, 16, 18, 17, 19])


@pytest.fixture
def sample_ohlc():
    data = {
        "high":  [10, 12, 11, 13, 14, 15, 16, 17],
        "low":   [8, 9, 8, 10, 11, 12, 13, 14],
        "close": [9, 11, 10, 12, 13, 14, 15, 16],
    }
    return {k: pd.Series(v) for k, v in data.items()}


@pytest.fixture
def sample_indicator():
    """Фикстура с тестовым индикатором для API запросов"""
    return {
        "name": "SMA 14",
        "type": "sma",
        "period": 14,
        "color": "#FF0000"
    }


@pytest.fixture
def sample_candles():
    """Фикстура с тестовыми свечами для API тестов"""
    return [
        {
            "timestamp": 1625097600000,
            "open": 50000.0,
            "high": 51000.0,
            "low": 49000.0,
            "close": 50500.0,
            "volume": 100.0,
            "turnover": 5000000.0
        },
        {
            "timestamp": 1625184000000,
            "open": 50500.0,
            "high": 52000.0,
            "low": 50000.0,
            "close": 51500.0,
            "volume": 150.0,
            "turnover": 7500000.0
        },
        {
            "timestamp": 1625270400000,
            "open": 51500.0,
            "high": 53000.0,
            "low": 51000.0,
            "close": 52500.0,
            "volume": 200.0,
            "turnover": 10000000.0
        }
    ]


@pytest.fixture
def mock_candles(sample_ohlc):
    """Подменяем глобальные candles для calculate()"""
    memory.candles.clear()

    for i in range(len(sample_ohlc["close"])):
        memory.candles.append({
            "high": float(sample_ohlc["high"].iloc[i]),
            "low": float(sample_ohlc["low"].iloc[i]),
            "close": float(sample_ohlc["close"].iloc[i]),
        })

    yield memory.candles
    memory.candles.clear()


@pytest.fixture(autouse=True)
def mock_db_session():
    """Фикстура для доступа к замоканной сессии в тестах"""
    return mock_session