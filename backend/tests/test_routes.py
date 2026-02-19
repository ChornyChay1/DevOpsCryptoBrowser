import pytest
from unittest.mock import patch, AsyncMock, MagicMock


# =====================================================
# CREATE
# =====================================================

def test_create_indicator(client, sample_indicator):

    # создаём мок-сессию
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    async def refresh_side_effect(ind):
        ind.id = 1

    mock_session.refresh.side_effect = refresh_side_effect

    # мок get_session_local
    with patch("api.indicator_routes.get_session_local") as mock_get_session_local:

        # get_session_local() → возвращает фабрику
        # фабрика() → возвращает mock_session
        mock_get_session_local.return_value = MagicMock(
            return_value=mock_session
        )

        # мок recalc_indicator
        with patch(
            "api.indicator_routes.recalc_indicator",
            new_callable=AsyncMock
        ) as mock_recalc:

            resp = client.post("/indicator", json=sample_indicator)

    assert resp.status_code == 200
    data = resp.json()

    assert "id" in data
    assert isinstance(data["id"], int)

    mock_recalc.assert_called_once()
