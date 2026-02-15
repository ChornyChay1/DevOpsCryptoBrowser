import pandas as pd
import numpy as np
from state.memory import candles
from utils.constants import Indicators
from core.logging import get_logger
class IndicatorsCalculator: 
    _logger = get_logger("IndicatorCalculator")


    @staticmethod
    def calc_sma(series, period):
        return series.rolling(period).mean().tolist()

    @staticmethod
    def calc_ema(series, period):
        return series.ewm(span=period, adjust=False).mean().tolist()

    @staticmethod
    def calc_rsi(series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calc_wma(series, period):
        weights = np.arange(1, period + 1)
        return series.rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

    @staticmethod
    def calc_roc(series, period=12):
        return ((series - series.shift(period)) / series.shift(period)) * 100

    @staticmethod
    def calc_momentum(series, period=10):
        return series - series.shift(period)

    @staticmethod
    def calc_cci(high, low, close, period=20):
        typical_price = (high + low + close) / 3
        sma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.fabs(x - x.mean()).mean(), raw=False)
        return (typical_price - sma) / (0.015 * mad.replace(0, np.nan))

    @staticmethod
    def calc_atr(high, low, close, period=14):
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    @staticmethod
    def calc_williams_r(high, low, close, period=14):
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        return -100 * (highest_high - close) / (highest_high - lowest_low).replace(0, np.nan)
    
    @classmethod
    def calculate(cls, ind_type, close, period, high = None, low = None):
        df = pd.DataFrame(candles)
        values = []
        try:
            if ind_type == Indicators.SMA:
                values = cls.calc_sma(close, period)
            
            elif ind_type == Indicators.EMA:
                values = cls.calc_ema(close, period)
            
            elif ind_type == Indicators.RSI:
                values = cls.calc_rsi(close, period)
            
            elif ind_type == Indicators.WMA:
                values = cls.calc_wma(close, period)
            
            elif ind_type == Indicators.ROC:
                values = cls.calc_roc(close, period)
            
            elif ind_type == Indicators.MOMENTUM:
                values = cls.calc_momentum(close, period)
            
            elif ind_type in ("cci", "atr", "williams_r"):
                high, low = df["high"], df["low"]
                if ind_type == Indicators.CCI:
                    values = cls.calc_cci(high, low, close, period)
                elif ind_type == Indicators.ATR:
                    values = cls.calc_atr(high, low, close, period)
                elif ind_type == Indicators.WILLIAMS_R:
                    values = cls.calc_williams_r(high, low, close, period)
            cls._logger.debug(f"The indicator {ind_type} value has been calculated successfully: {values}")
        
        except Exception as exception:
            cls._logger.exception(f"Exception {exception} while calculating indicator with type {ind_type}")
            
        return values