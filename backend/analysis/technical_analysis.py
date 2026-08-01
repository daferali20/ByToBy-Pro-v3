"""
ByToBy Pro v3
Technical Analysis Engine

Calculates technical indicators and trading signals.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

try:
    import pandas_ta as ta
except ImportError:
    ta = None


class TechnicalAnalysis:

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()

    # --------------------------------------------------

    def moving_averages(self):

        self.df["SMA20"] = self.df["close"].rolling(20).mean()
        self.df["SMA50"] = self.df["close"].rolling(50).mean()
        self.df["SMA100"] = self.df["close"].rolling(100).mean()
        self.df["SMA200"] = self.df["close"].rolling(200).mean()

        self.df["EMA9"] = self.df["close"].ewm(span=9).mean()
        self.df["EMA21"] = self.df["close"].ewm(span=21).mean()
        self.df["EMA50"] = self.df["close"].ewm(span=50).mean()

    # --------------------------------------------------

    def rsi(self):

        if ta:
            self.df["RSI"] = ta.rsi(
                self.df["close"],
                length=14
            )
            return

        delta = self.df["close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss

        self.df["RSI"] = 100 - (100 / (1 + rs))

    # --------------------------------------------------

    def macd(self):

        ema12 = self.df["close"].ewm(span=12).mean()
        ema26 = self.df["close"].ewm(span=26).mean()

        self.df["MACD"] = ema12 - ema26
        self.df["MACD_SIGNAL"] = self.df["MACD"].ewm(span=9).mean()
        self.df["MACD_HIST"] = (
            self.df["MACD"] -
            self.df["MACD_SIGNAL"]
        )

    # --------------------------------------------------

    def bollinger(self):

        sma = self.df["close"].rolling(20).mean()
        std = self.df["close"].rolling(20).std()

        self.df["BB_UPPER"] = sma + std * 2
        self.df["BB_LOWER"] = sma - std * 2
        self.df["BB_WIDTH"] = (
            (self.df["BB_UPPER"] - self.df["BB_LOWER"])
            / sma
        ) * 100

    # --------------------------------------------------

    def atr(self):

        high = self.df["high"]
        low = self.df["low"]
        close = self.df["close"]

        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()

        tr = pd.concat(
            [tr1, tr2, tr3],
            axis=1
        ).max(axis=1)

        self.df["ATR"] = tr.rolling(14).mean()

    # --------------------------------------------------

    def volume(self):

        self.df["VOL20"] = (
            self.df["volume"]
            .rolling(20)
            .mean()
        )

        self.df["RVOL"] = (
            self.df["volume"]
            / self.df["VOL20"]
        )

    # --------------------------------------------------

    def trend(self):

        last = self.df.iloc[-1]

        bullish = (
            last["EMA9"] >
            last["EMA21"] >
            last["EMA50"]
        )

        bearish = (
            last["EMA9"] <
            last["EMA21"] <
            last["EMA50"]
        )

        if bullish:
            return "Bullish"

        if bearish:
            return "Bearish"

        return "Sideways"

    # --------------------------------------------------

    def golden_cross(self):

        sma50 = self.df["SMA50"]
        sma200 = self.df["SMA200"]

        cross = (
            (sma50.shift(1) < sma200.shift(1))
            &
            (sma50 > sma200)
        )

        return bool(cross.iloc[-1])

    # --------------------------------------------------

    def death_cross(self):

        sma50 = self.df["SMA50"]
        sma200 = self.df["SMA200"]

        cross = (
            (sma50.shift(1) > sma200.shift(1))
            &
            (sma50 < sma200)
        )

        return bool(cross.iloc[-1])

    # --------------------------------------------------

    def support(self, lookback=30):

        return float(
            self.df["low"]
            .tail(lookback)
            .min()
        )

    # --------------------------------------------------

    def resistance(self, lookback=30):

        return float(
            self.df["high"]
            .tail(lookback)
            .max()
        )

    # --------------------------------------------------

    def analyze(self):

        self.moving_averages()
        self.rsi()
        self.macd()
        self.bollinger()
        self.atr()
        self.volume()

        last = self.df.iloc[-1]

        return {

            "price": round(last["close"], 2),

            "trend": self.trend(),

            "rsi": round(last["RSI"], 2),

            "macd": round(last["MACD"], 3),

            "macd_signal": round(
                last["MACD_SIGNAL"], 3
            ),

            "atr": round(last["ATR"], 2),

            "bb_width": round(
                last["BB_WIDTH"], 2
            ),

            "relative_volume": round(
                last["RVOL"], 2
            ),

            "golden_cross": self.golden_cross(),

            "death_cross": self.death_cross(),

            "support": self.support(),

            "resistance": self.resistance(),

            "data": self.df
        }


if __name__ == "__main__":

    from backend.data_providers.market_data import market_data

    df = market_data.history("NVDA")

    ta_engine = TechnicalAnalysis(df)

    result = ta_engine.analyze()

    print(result)
