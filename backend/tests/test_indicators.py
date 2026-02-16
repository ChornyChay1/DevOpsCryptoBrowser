import pytest
import pandas as pd
import numpy as np
from services.indicators import IndicatorsCalculator


class TestIndicatorsCalculator:
    """Тесты для класса IndicatorsCalculator"""

    @pytest.fixture
    def sample_series(self):
        """Фикстура с тестовыми данными в виде pandas Series"""
        return pd.Series([10, 12, 11, 13, 15, 14, 16, 18, 17, 19])

    def test_calculate_sma(self, sample_series):
        """Тест расчета SMA"""
        period = 5
        sma = IndicatorsCalculator.calc_sma(sample_series, period)

        assert len(sma) == len(sample_series)

        # Проверяем типы (метод возвращает список)
        assert isinstance(sma, list)

        # Проверяем, что первые period-1 значений NaN
        for i in range(period - 1):
            assert pd.isna(sma[i])

        # Проверяем первое вычисленное значение
        expected_first = sample_series.iloc[0:period].mean()
        assert sma[period - 1] == expected_first

        # Проверяем конкретное значение (индекс 4 - это 5-й элемент, 0-based)
        assert sma[4] == sum([10, 12, 11, 13, 15]) / 5

    def test_calculate_sma_empty_data(self):
        """Тест SMA с пустыми данными"""
        empty_series = pd.Series([])
        sma = IndicatorsCalculator.calc_sma(empty_series, 14)
        assert sma == []

    def test_calculate_sma_single_value(self):
        """Тест SMA с одним значением"""
        single_series = pd.Series([10])
        sma = IndicatorsCalculator.calc_sma(single_series, 5)
        assert len(sma) == 1
        assert pd.isna(sma[0])

    def test_calculate_ema(self, sample_series):
        """Тест расчета EMA"""
        period = 5
        ema = IndicatorsCalculator.calc_ema(sample_series, period)

        assert len(ema) == len(sample_series)
        assert isinstance(ema, list)

        # Первое значение должно быть равно первому элементу ряда
        assert ema[0] == sample_series.iloc[0]

        # Проверяем формулу EMA для второго значения
        # EMA = Price(t) * k + EMA(y) * (1 - k) где k = 2/(n+1)
        multiplier = 2 / (period + 1)
        expected_second = (sample_series.iloc[1] - ema[0]) * multiplier + ema[0]
        assert abs(ema[1] - expected_second) < 0.0001

    def test_calculate_rsi(self):
        """Тест расчета RSI"""
        # Используем данные, которые дадут предсказуемый RSI
        prices = pd.Series([
            44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
            45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00
        ])
        period = 14

        rsi = IndicatorsCalculator.calc_rsi(prices, period)

        assert len(rsi) == len(prices)
        assert isinstance(rsi, pd.Series)  # RSI возвращает Series

        # Проверяем, что первые period значений NaN
        for i in range(period):
            assert pd.isna(rsi.iloc[i])

        # RSI должен быть между 0 и 100
        valid_rsi = rsi.dropna()
        assert all(0 <= x <= 100 for x in valid_rsi)

        # Проверяем примерное значение RSI (известно из практики)
        assert 60 <= valid_rsi.iloc[0] <= 80  # Обычно RSI в этом диапазоне

    def test_calculate_wma(self, sample_series):
        """Тест расчета WMA (Weighted Moving Average)"""
        period = 5
        wma = IndicatorsCalculator.calc_wma(sample_series, period)

        assert len(wma) == len(sample_series)
        assert isinstance(wma, pd.Series)

        # Проверяем первые period-1 значений NaN
        for i in range(period - 1):
            assert pd.isna(wma.iloc[i])

        # Ручной расчет WMA для первых 5 значений
        weights = np.arange(1, period + 1)
        values = sample_series.iloc[0:period].values
        expected = np.dot(values, weights) / weights.sum()
        assert abs(wma.iloc[period - 1] - expected) < 0.0001

    def test_calculate_roc(self, sample_series):
        """Тест расчета ROC (Rate of Change)"""
        period = 3
        roc = IndicatorsCalculator.calc_roc(sample_series, period)

        assert len(roc) == len(sample_series)
        assert isinstance(roc, pd.Series)

        # Первые period значений должны быть NaN
        for i in range(period):
            assert pd.isna(roc.iloc[i])

        # Проверяем формулу ROC
        # ROC = ((Price - Price-n) / Price-n) * 100
        expected = ((15 - 11) / 11) * 100  # Для индекса 4 (значение 15, период 3 назад = 11)
        assert abs(roc.iloc[period] - expected) < 0.0001

    def test_calculate_momentum(self, sample_series):
        """Тест расчета Momentum"""
        period = 3
        momentum = IndicatorsCalculator.calc_momentum(sample_series, period)

        assert len(momentum) == len(sample_series)
        assert isinstance(momentum, pd.Series)

        # Первые period значений должны быть NaN
        for i in range(period):
            assert pd.isna(momentum.iloc[i])

        # Проверяем формулу Momentum
        expected = 15 - 11  # Для индекса 4 (15 - 11)
        assert momentum.iloc[period] == expected

    def test_calculate_cci(self):
        """Тест расчета CCI (Commodity Channel Index)"""
        # Тестовые данные
        high = pd.Series([10, 11, 12, 13, 14, 15, 16, 17])
        low = pd.Series([8, 9, 10, 11, 12, 13, 14, 15])
        close = pd.Series([9, 10, 11, 12, 13, 14, 15, 16])
        period = 5

        cci = IndicatorsCalculator.calc_cci(high, low, close, period)

        assert len(cci) == len(close)
        assert isinstance(cci, pd.Series)

        # Первые period-1 значений NaN
        for i in range(period - 1):
            assert pd.isna(cci.iloc[i])

    def test_calculate_atr(self):
        """Тест расчета ATR (Average True Range)"""
        # Тестовые данные
        high = pd.Series([10, 12, 11, 13, 14, 15, 16])
        low = pd.Series([8, 9, 8, 10, 11, 12, 13])
        close = pd.Series([9, 11, 10, 12, 13, 14, 15])
        period = 5

        atr = IndicatorsCalculator.calc_atr(high, low, close, period)

        assert len(atr) == len(close)
        assert isinstance(atr, pd.Series)

        # Первые period-1 значений NaN
        for i in range(period - 1):
            assert pd.isna(atr.iloc[i])

    def test_calculate_williams_r(self):
        """Тест расчета Williams %R"""
        # Тестовые данные
        high = pd.Series([10, 12, 11, 13, 14, 15, 16, 17])
        low = pd.Series([8, 9, 8, 10, 11, 12, 13, 14])
        close = pd.Series([9, 11, 10, 12, 13, 14, 15, 16])
        period = 5

        williams_r = IndicatorsCalculator.calc_williams_r(high, low, close, period)

        assert len(williams_r) == len(close)
        assert isinstance(williams_r, pd.Series)

        # Williams %R должен быть между -100 и 0
        valid_values = williams_r.dropna()
        assert all(-100 <= x <= 0 for x in valid_values)

    def test_calculate_method_with_close_only(self, sample_series):
        """Тест метода calculate для индикаторов, использующих только close"""
        period = 5

        # Тест SMA
        sma = IndicatorsCalculator.calculate("sma", sample_series, period)
        assert len(sma) == len(sample_series)

        # Тест EMA
        ema = IndicatorsCalculator.calculate("ema", sample_series, period)
        assert len(ema) == len(sample_series)

        # Тест RSI
        rsi = IndicatorsCalculator.calculate("rsi", sample_series, 5)
        assert len(rsi) == len(sample_series)

    def test_calculate_method_with_error_handling(self, sample_series, caplog):
        """Тест обработки ошибок в методе calculate"""
        # Передаем неверный тип индикатора
        result = IndicatorsCalculator.calculate("invalid_type", sample_series, 5)

        # Должен вернуть пустой список
        assert result == []

        # Проверяем, что ошибка была залогирована
        assert "Exception" in caplog.text

    @pytest.mark.parametrize("indicator_type,expected_nans", [
        ("sma", 4),  # Для периода 5, первые 4 значения NaN
        ("ema", 0),  # EMA не дает NaN в начале
        ("rsi", 5),  # RSI дает NaN для всего периода
    ])
    def test_indicator_nan_patterns(self, sample_series, indicator_type, expected_nans):
        """Параметризованный тест для проверки NaN в начале"""
        period = 5

        result = IndicatorsCalculator.calculate(indicator_type, sample_series, period)

        if indicator_type == "rsi":
            # RSI возвращает Series
            nans = sum(pd.isna(result))
        else:
            # Остальные возвращают списки
            nans = sum(pd.isna(x) for x in result)

        assert nans == expected_nans