import pytest
from services.indicators import IndicatorsCalculator


def test_calculate_indicators(sample_candles):
    """Тест расчета всех индикаторов"""
    indicators_config = [
        {"id": "1", "type": "sma", "period": 14},
        {"id": "2", "type": "ema", "period": 14}
    ]

    result = IndicatorsCalculator.calculate(sample_candles, indicators_config)

    assert "indicators" in result
    assert "1" in result["indicators"]
    assert "2" in result["indicators"]

    # Проверка, что значения не None
    for candle in result["candles"]:
        if "indicators" in candle:
            for ind_id in indicators_config:
                assert ind_id["id"] in candle["indicators"]