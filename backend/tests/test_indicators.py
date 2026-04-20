from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from models.indicator import IndicatorDB
from services.indicators import IndicatorsCalculator
from services.indicators import clean
from services.indicators import recalc_all_indicators
from services.indicators import recalc_indicator
from utils.constants import Indicators


# --------------------------
# Фикстуры
# --------------------------
@pytest.fixture
def sample_series():
    """Тестовая серия для индикаторов"""
    return pd.Series([10, 12, 11, 13, 15, 14, 16, 18, 17, 19])


@pytest.fixture
def mock_candles(monkeypatch):
    """Мокаем candles для calculate()"""
    from state import memory
    memory.candles = [{"close": v} for v in range(10)]
    yield
    memory.candles = []


# =========================
# SMA
# =========================
def test_sma_basic(sample_series):
    period = 5
    sma = IndicatorsCalculator.calc_sma(sample_series, period)

    assert len(sma) == len(sample_series)
    assert isinstance(sma, list)

    # Первые period-1 значений должны быть NaN
    for i in range(period - 1):
        assert pd.isna(sma[i])

    # Проверка первого вычисленного значения
    expected = sample_series.iloc[:period].mean()
    assert sma[period - 1] == expected


def test_sma_empty():
    sma = IndicatorsCalculator.calc_sma(pd.Series(dtype=float), 5)
    assert sma == []


# =========================
# EMA
# =========================
def test_ema_formula(sample_series):
    period = 5
    ema = IndicatorsCalculator.calc_ema(sample_series, period)

    # Первое значение = первый элемент серии
    assert ema[0] == sample_series.iloc[0]

    # Проверка формулы EMA для второго значения
    k = 2 / (period + 1)
    expected = (sample_series.iloc[1] - ema[0]) * k + ema[0]
    assert abs(ema[1] - expected) < 1e-6


# =========================
# WMA
# =========================
def test_wma_manual(sample_series):
    period = 5
    wma = IndicatorsCalculator.calc_wma(sample_series, period)

    weights = np.arange(1, period + 1)
    expected = np.dot(sample_series.iloc[:period], weights) / weights.sum()

    # Проверка пятого значения
    assert abs(wma.iloc[period - 1] - expected) < 1e-6


# =========================
# calculate() для close-only
# =========================
def test_calculate_close_only(sample_series, mock_candles):
    period = 5

    sma = IndicatorsCalculator.calculate(Indicators.SMA, sample_series, period)
    ema = IndicatorsCalculator.calculate(Indicators.EMA, sample_series, period)
    wma = IndicatorsCalculator.calculate(Indicators.WMA, sample_series, period)

    assert len(sma) == len(sample_series)
    assert len(ema) == len(sample_series)
    assert len(wma) == len(sample_series)


# =========================
# Проверка NaN в начале
# =========================
@pytest.mark.parametrize(
    "indicator,expected_nans",
    [
        (Indicators.SMA, 4),  # period-1
        (Indicators.EMA, 0),
        (Indicators.WMA, 4),  # period-1
    ],
)
def test_nan_patterns(sample_series, indicator, expected_nans, mock_candles):
    result = IndicatorsCalculator.calculate(indicator, sample_series, 5)

    if isinstance(result, pd.Series):
        nans = result.isna().sum()
    else:
        nans = sum(pd.isna(x) for x in result)

    assert nans == expected_nans


def test_clean_normal_values():
    """Тест с нормальными значениями"""
    values = [1.0, 2.5, 3.7, 4.2]
    result = clean(values)
    assert result == [1.0, 2.5, 3.7, 4.2]


def test_clean_with_none():
    """Тест с None значениями"""
    values = [1.0, None, 3.0, None, 5.0]
    result = clean(values)
    assert result == [1.0, None, 3.0, None, 5.0]


def test_clean_with_infinity():
    """Тест с бесконечными значениями"""
    values = [1.0, float('inf'), 3.0, float('-inf'), 5.0]
    result = clean(values)
    assert result == [1.0, None, 3.0, None, 5.0]


def test_clean_with_nan():
    """Тест с NaN значениями"""
    values = [1.0, float('nan'), 3.0, float('nan'), 5.0]
    result = clean(values)
    # math.isnan не работает с float('nan'), нужно использовать другой подход
    assert result[0] == 1.0
    assert result[1] is None
    assert result[2] == 3.0
    assert result[3] is None
    assert result[4] == 5.0


def test_clean_mixed_invalid():
    """Тест со смешанными некорректными значениями"""
    values = [None, float('inf'), float('nan'), float('-inf')]
    result = clean(values)
    assert all(v is None for v in result)


def test_clean_empty():
    """Тест с пустым списком"""
    result = clean([])
    assert result == []


# =========================
# Тесты для recalc_indicator
# =========================
@pytest.mark.asyncio
async def test_recalc_indicator_empty_candles():
    """Тест когда нет свечей"""
    with patch('services.indicators.candles', []):
        ind = IndicatorDB(id=1, type=Indicators.SMA, period=14)
        indicator_values = {}

        with patch('services.indicators.indicator_values', indicator_values):
            await recalc_indicator(ind)
            assert indicator_values[1] == []


@pytest.mark.asyncio
async def test_recalc_indicator_with_candles():
    """Тест с наличием свечей"""
    mock_candles = [
        {"close": 10}, {"close": 12}, {"close": 11}, {"close": 13}, {"close": 15}
    ]

    with patch('services.indicators.candles', mock_candles):
        ind = IndicatorDB(id=1, type=Indicators.SMA, period=3)
        indicator_values = {}

        with patch('services.indicators.indicator_values', indicator_values):
            await recalc_indicator(ind)

            # Проверяем что значение было установлено
            assert 1 in indicator_values
            assert len(indicator_values[1]) == len(mock_candles)


@pytest.mark.asyncio
async def test_recalc_indicator_default_period():
    """Тест с периодом по умолчанию"""
    mock_candles = [{"close": i} for i in range(20)]

    with patch('services.indicators.candles', mock_candles):
        ind = IndicatorDB(id=1, type=Indicators.EMA, period=None)  # Должен стать 14
        indicator_values = {}

        with patch('services.indicators.indicator_values', indicator_values):
            await recalc_indicator(ind)
            assert 1 in indicator_values


@pytest.mark.asyncio
async def test_recalc_indicator_different_types():
    """Тест с разными типами индикаторов"""
    mock_candles = [{"close": i} for i in range(10)]

    indicator_types = [Indicators.SMA, Indicators.EMA, Indicators.WMA]

    for ind_type in indicator_types:
        with patch('services.indicators.candles', mock_candles):
            ind = IndicatorDB(id=1, type=ind_type, period=5)
            indicator_values = {}

            with patch('services.indicators.indicator_values', indicator_values):
                await recalc_indicator(ind)
                assert 1 in indicator_values


@pytest.mark.asyncio
async def test_recalc_all_indicators_no_indicators():
    """Тест когда нет индикаторов в БД"""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = []
    mock_session.execute.return_value = mock_result

    mock_session_local = MagicMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session

    with patch('services.indicators.get_session_local', return_value=mock_session_local):
        with patch('services.indicators.recalc_indicator') as mock_recalc:
            await recalc_all_indicators()
            mock_recalc.assert_not_called()


@pytest.mark.asyncio
async def test_recalc_all_indicators_with_indicators():
    """Тест с несколькими индикаторами"""
    indicators = [
        IndicatorDB(id=1, type=Indicators.SMA, period=10),
        IndicatorDB(id=2, type=Indicators.EMA, period=20),
        IndicatorDB(id=3, type=Indicators.WMA, period=5),
    ]

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = indicators
    mock_session.execute.return_value = mock_result

    mock_session_local = MagicMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session

    with patch('services.indicators.get_session_local', return_value=mock_session_local):
        with patch('services.indicators.recalc_indicator') as mock_recalc:
            await recalc_all_indicators()
            assert mock_recalc.call_count == len(indicators)

            # Проверяем что каждый индикатор был передан
            calls = [call[0][0] for call in mock_recalc.call_args_list]
            assert set(calls) == set(indicators)


@pytest.mark.asyncio
async def test_recalc_all_indicators_db_error():
    """Тест обработки ошибки БД"""
    mock_session = AsyncMock()
    mock_session.execute.side_effect = Exception("Database connection error")

    mock_session_local = MagicMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session

    with patch('services.indicators.get_session_local', return_value=mock_session_local):
        with patch('services.indicators.recalc_indicator'):
            with pytest.raises(Exception) as exc_info:
                await recalc_all_indicators()
            assert "Database connection error" in str(exc_info.value)
