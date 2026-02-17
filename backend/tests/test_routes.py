import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from state.memory import indicator_values, candles


# =====================================================
# CREATE
# =====================================================

def test_create_indicator(client, sample_indicator):
    # Мокаем сессию БД и recalc_indicator
    with patch("api.indicator_routes.SessionLocal") as mock_session_local:
        # Настраиваем мок сессии
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session_local.return_value = mock_session

        # Мокаем методы сессии
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Устанавливаем id для созданного индикатора
        async def refresh_side_effect(ind):
            ind.id = 1
            return None

        mock_session.refresh.side_effect = refresh_side_effect

        # Патчим recalc_indicator
        with patch("api.indicator_routes.recalc_indicator", new_callable=AsyncMock) as mock_recalc:
            resp = client.post("/indicator", json=sample_indicator)

    assert resp.status_code == 200
    data = resp.json()

    assert "id" in data
    assert isinstance(data["id"], int)

    mock_recalc.assert_called_once()