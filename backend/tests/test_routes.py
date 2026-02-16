import pytest
from unittest.mock import Mock, patch


def test_get_data(client, sample_candles):
    """Тест получения данных"""
    with patch('app.routes.fetch_candles') as mock_fetch:
        mock_fetch.return_value = sample_candles

        response = client.get("/data")

        assert response.status_code == 200
        data = response.json()
        assert "candles" in data
        assert "indicators" in data
        assert len(data["candles"]) == len(sample_candles)


def test_create_indicator(client, sample_indicator):
    """Тест создания индикатора"""
    response = client.post("/indicator", json=sample_indicator)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_indicator["name"]
    assert data["type"] == sample_indicator["type"]
    assert "id" in data


def test_create_indicator_invalid_data(client):
    """Тест создания индикатора с невалидными данными"""
    invalid_data = {"name": "", "type": "invalid"}
    response = client.post("/indicator", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_update_indicator(client, sample_indicator):
    """Тест обновления индикатора"""
    # Сначала создаем индикатор
    create_response = client.post("/indicator", json=sample_indicator)
    indicator_id = create_response.json()["id"]

    # Обновляем
    update_data = {**sample_indicator, "name": "Updated SMA", "color": "#ff0000"}
    response = client.put(f"/indicator/{indicator_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated SMA"
    assert data["color"] == "#ff0000"


def test_delete_indicator(client, sample_indicator):
    """Тест удаления индикатора"""
    # Создаем
    create_response = client.post("/indicator", json=sample_indicator)
    indicator_id = create_response.json()["id"]

    # Удаляем
    delete_response = client.delete(f"/indicator/{indicator_id}")
    assert delete_response.status_code == 200

    # Проверяем, что удален
    get_response = client.get("/data")
    indicators = get_response.json()["indicators"]
    assert not any(i["id"] == indicator_id for i in indicators)


def test_delete_nonexistent_indicator(client):
    """Тест удаления несуществующего индикатора"""
    response = client.delete("/indicator/99999")
    assert response.status_code == 404