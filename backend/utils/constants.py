from enum import Enum


class Indicators(str, Enum):
    """Поддерживаемые типы индикаторов (только с одним параметром period)"""
    
    SMA = "sma"
    EMA = "ema"
    WMA = "wma"
    RSI = "rsi"
    ROC = "roc"
    MOMENTUM = "momentum"
    WILLIAMS_R = "williams_r"
    ATR = "atr"
    CCI = "cci"