# test_candles.py - исправленная версия

from unittest.mock import MagicMock, AsyncMock, patch

import httpx
import pytest
from services.candles import fetch_candles


# =========================
# Фикстуры
# =========================
@pytest.fixture
def mock_candles_state():
    """Фикстура для очистки и мока состояния candles"""
    from state import memory
    # Сохраняем оригинальное состояние
    original_candles = memory.candles.copy() if memory.candles else []
    # Очищаем
    memory.candles = []
    yield memory.candles
    # Восстанавливаем
    memory.candles = original_candles


@pytest.fixture
def sample_bybit_response():
    """Пример ответа от Bybit API"""
    return {
        "result": {
            "list": [
                ["1000000", "50000", "51000", "49000", "50500", "100", "5000000"],
                ["1000060", "50500", "51500", "49500", "51000", "150", "7650000"],
                ["1000120", "51000", "52000", "50000", "51500", "120", "6180000"],
            ]
        }
    }


# =========================
# Тесты для fetch_candles
# =========================


@pytest.mark.asyncio
async def test_fetch_candles_empty_response(mock_candles_state):
    """Тест пустого ответа от API"""
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={"result": {"list": []}})

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('services.candles.httpx.AsyncClient', return_value=mock_client):
        with patch('services.candles.recalc_all_indicators', new=AsyncMock()) as mock_recalc:
            await fetch_candles()

            from state import memory
            # Свечей быть не должно
            assert len(memory.candles) == 0
            mock_recalc.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_candles_invalid_data(mock_candles_state):
    """Тест с некорректными данными"""
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={
        "result": {
            "list": [
                ["invalid", "not_number", "bad", "wrong", "data", "100", "5000000"],
            ]
        }
    })

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('services.candles.httpx.AsyncClient', return_value=mock_client):
        with patch('services.candles.recalc_all_indicators', new=AsyncMock()):
            # Должна быть ошибка при преобразовании в float
            with pytest.raises((ValueError, TypeError)):
                await fetch_candles()


@pytest.mark.asyncio
async def test_fetch_candles_api_error(mock_candles_state):
    """Тест ошибки API (сетевые проблемы)"""
    mock_client = MagicMock()
    mock_client.get = AsyncMock(side_effect=httpx.RequestError("Connection failed"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('services.candles.httpx.AsyncClient', return_value=mock_client):
        with pytest.raises(httpx.RequestError):
            await fetch_candles()


@pytest.mark.asyncio
async def test_fetch_candles_missing_result_key(mock_candles_state):
    """Тест ответа без ключа 'result'"""
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={"error": "Invalid request"})

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('services.candles.httpx.AsyncClient', return_value=mock_client):
        with pytest.raises(KeyError):
            await fetch_candles()


@pytest.mark.asyncio
async def test_fetch_candles_missing_list_key(mock_candles_state):
    """Тест ответа без ключа 'list'"""
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={"result": {}})

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('services.candles.httpx.AsyncClient', return_value=mock_client):
        with pytest.raises(KeyError):
            await fetch_candles()


@pytest.mark.asyncio
async def test_fetch_candles_partial_data(mock_candles_state):
    """Тест с частичными данными (не все колонки)"""
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={
        "result": {
            "list": [
                ["1000000", "50000", "51000", "49000"],  # Не хватает колонок
            ]
        }
    })

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('services.candles.httpx.AsyncClient', return_value=mock_client):
        with patch('services.candles.recalc_all_indicators', new=AsyncMock()):
            # Должна быть ошибка при создании DataFrame
            with pytest.raises(ValueError):
                await fetch_candles()


@pytest.mark.asyncio
async def test_fetch_candles_request_params():
    """Тест правильности параметров запроса"""
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={"result": {"list": []}})

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('services.candles.httpx.AsyncClient', return_value=mock_client):
        with patch('services.candles.get_bybit_url', return_value="https://api.bybit.com/v5/market/kline"):
            with patch('services.candles.recalc_all_indicators', new=AsyncMock()):
                await fetch_candles()

                # Проверяем параметры запроса
                call_args = mock_client.get.call_args
                assert call_args is not None
                assert call_args[0][0] == "https://api.bybit.com/v5/market/kline"

                params = call_args[1]["params"]
                assert params["category"] == "linear"
                assert params["symbol"] == "BTCUSDT"
                assert params["interval"] == "1"
                assert params["limit"] == 100


@pytest.mark.asyncio
async def test_fetch_candles_logging():
    """Тест логирования"""
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={"result": {"list": []}})

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch('services.candles.httpx.AsyncClient', return_value=mock_client):
        with patch('services.candles.recalc_all_indicators', new=AsyncMock()):
            with patch('services.candles._logger') as mock_logger:
                await fetch_candles()

                # Проверяем что логи были вызваны
                assert mock_logger.debug.call_count >= 2
