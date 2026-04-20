# test_routes_working.py - работающая версия с правильными патчами

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from app import app
from state.memory import candles, indicator_values

client = TestClient(app)


@pytest.fixture
def clear_memory():
    """Очистка памяти перед каждым тестом"""
    candles.clear()
    indicator_values.clear()
    yield
    candles.clear()
    indicator_values.clear()


# =========================
# Тесты для POST /indicator
# =========================
def test_create_indicator_success(clear_memory):
    """Тест успешного создания индикатора"""
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = mock_session

    # Патчим прямо в модуле api.indicator_routes
    with patch('api.indicator_routes.get_session_local', return_value=mock_sessionmaker):
        with patch('services.indicators.recalc_indicator', new=AsyncMock()):
            response = client.post(
                "/indicator",
                json={
                    "name": "SMA 14",
                    "type": "sma",
                    "period": 14,
                    "color": "#FF0000"
                }
            )
            assert response.status_code == 200


def test_create_indicator_missing_name(clear_memory):
    """Тест создания индикатора без имени"""
    response = client.post(
        "/indicator",
        json={"type": "sma", "period": 14}
    )
    assert response.status_code == 422


# =========================
# Тесты для PUT /indicator
# =========================
def test_update_indicator_not_found(clear_memory):
    """Тест обновления несуществующего индикатора"""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = mock_session

    with patch('api.indicator_routes.get_session_local', return_value=mock_sessionmaker):
        response = client.put("/indicator/999", json={"name": "New Name"})
        assert response.status_code == 404


def test_update_indicator_success(clear_memory):
    """Тест успешного обновления индикатора"""
    mock_indicator = MagicMock()
    mock_indicator.id = 1
    mock_indicator.name = "Old Name"
    mock_indicator.type = "sma"
    mock_indicator.period = 10
    mock_indicator.color = "#000000"

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_indicator)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = mock_session

    with patch('api.indicator_routes.get_session_local', return_value=mock_sessionmaker):
        with patch('services.indicators.recalc_indicator', new=AsyncMock()):
            response = client.put(
                "/indicator/1",
                json={"name": "New Name", "period": 20}
            )
            assert response.status_code == 200


# =========================
# Тесты для DELETE /indicator
# =========================
def test_delete_indicator_success(clear_memory):
    """Тест успешного удаления индикатора"""
    indicator_values[1] = [10, 20, 30]

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = mock_session

    with patch('api.indicator_routes.get_session_local', return_value=mock_sessionmaker):
        response = client.delete("/indicator/1")
        assert response.status_code == 200
        assert 1 not in indicator_values


# =========================
# Тесты для GET /data
# =========================
def test_get_data_empty(clear_memory):
    """Тест получения данных когда нет свечей и индикаторов"""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all = MagicMock(return_value=[])
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = mock_session

    with patch('api.indicator_routes.get_session_local', return_value=mock_sessionmaker):
        with patch('services.indicators.clean', side_effect=lambda x: x):
            response = client.get("/data")
            assert response.status_code == 200
            data = response.json()
            assert "candles" in data
            assert "indicators" in data


def test_get_data_with_candles(clear_memory):
    """Тест получения данных со свечами"""
    candles.append({"timestamp": 1000, "close": 100})

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all = MagicMock(return_value=[])
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = mock_session

    with patch('api.indicator_routes.get_session_local', return_value=mock_sessionmaker):
        with patch('services.indicators.clean', side_effect=lambda x: x):
            response = client.get("/data")
            assert response.status_code == 200
            assert len(response.json()["candles"]) == 1


def test_get_data_with_indicators(clear_memory):
    """Тест получения данных с индикаторами"""
    # Мок индикаторов из БД
    mock_indicator1 = MagicMock()
    mock_indicator1.id = 1
    mock_indicator1.name = "SMA 14"
    mock_indicator1.type = "sma"
    mock_indicator1.period = 14
    mock_indicator1.color = "#FF0000"

    mock_indicator2 = MagicMock()
    mock_indicator2.id = 2
    mock_indicator2.name = "EMA 20"
    mock_indicator2.type = "ema"
    mock_indicator2.period = 20
    mock_indicator2.color = "#00FF00"

    # Добавляем свечи
    candles.extend([
        {"timestamp": 1000, "close": 100},
        {"timestamp": 2000, "close": 110},
    ])

    # Добавляем значения индикаторов
    indicator_values[1] = [None, 105]
    indicator_values[2] = [100, 110]

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all = MagicMock(return_value=[mock_indicator1, mock_indicator2])
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_sessionmaker = MagicMock()
    mock_sessionmaker.return_value = mock_session

    with patch('api.indicator_routes.get_session_local', return_value=mock_sessionmaker):
        with patch('services.indicators.clean', side_effect=lambda x: x):
            response = client.get("/data")
            assert response.status_code == 200
            data = response.json()
            assert len(data["indicators"]) == 2


# =========================
# Тесты для проверки clean функции
# =========================
def test_clean_removes_infinity():
    """Тест что clean убирает бесконечность"""
    from services.indicators import clean
    result = clean([1.0, float('inf'), 2.0, float('-inf')])
    assert result == [1.0, None, 2.0, None]


def test_clean_removes_nan():
    """Тест что clean убирает NaN"""
    from services.indicators import clean
    import math
    result = clean([1.0, float('nan'), 2.0])
    assert result[0] == 1.0
    assert result[1] is None
    assert result[2] == 2.0


def test_clean_preserves_none():
    """Тест что clean сохраняет None"""
    from services.indicators import clean
    result = clean([1.0, None, 2.0])
    assert result == [1.0, None, 2.0]