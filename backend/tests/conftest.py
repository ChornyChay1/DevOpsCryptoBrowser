import pytest
from fastapi.testclient import TestClient
from app import app
import json
import os

@pytest.fixture
def client():
    """Тестовый клиент FastAPI"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def sample_candles():
    """Пример данных свечей для тестов"""
    return [
        {
            "timestamp": 1704067200000,
            "open": 50000.0,
            "high": 51000.0,
            "low": 49000.0,
            "close": 50500.0,
            "volume": 100.0
        },
        {
            "timestamp": 1704067260000,
            "open": 50500.0,
            "high": 51500.0,
            "low": 50300.0,
            "close": 51200.0,
            "volume": 150.0
        },
        # Добавьте больше свечей по необходимости
    ]

@pytest.fixture
def sample_indicator():
    """Пример данных индикатора"""
    return {
        "name": "SMA 14",
        "type": "sma",
        "period": 14,
        "color": "#00c853"
    }

@pytest.fixture
def temp_db():
    """Временная БД для тестов"""
    # Здесь можно настроить тестовую БД
    yield
    # Очистка после тестов