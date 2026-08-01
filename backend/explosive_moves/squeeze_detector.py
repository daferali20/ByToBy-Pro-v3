"""
ByToBy Pro v3
AI Squeeze Detection Engine

Detects volatility compression before explosive moves.
"""

from __future__ import annotations

import pandas as pd
import numpy as np

try:
    import pandas_ta as ta
except ImportError:
    ta = None


class SqueezeDetector:

    def __init__(self, bb_length=20, bb_std=2, kc_length=20, kc_mult=1.5):
        self.bb_length = bb_length
        self.bb_std = bb_std
        self.kc_length = kc_length
        self.kc_mult = kc_mult

    def _true_range(self, df: pd.DataFrame):
        high = df["High"]
        low = df["Low"]
        close = df["Close"]

        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()

        return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    def calculate(self, df: pd.DataFrame):

        data = df.copy()

        if ta:

            bb = ta.bbands(
                data["Close"],
                length=self.bb_length,
                std=self.bb_std
            )

            atr = ta.atr(
                data["High"],
                data["Low"],
                data["Close"],
                length=self.kc_length
            )

        else:

            sma = data["Close"].rolling(self.bb_length).mean()
            std = data["Close"].rolling(self.bb_length).std()

            bb = pd.DataFrame({
                "BBL": sma - std * self.bb_std,
                "BBM": sma,
                "BBU": sma + std * self.bb_std
            })

            atr = self._true_range(data).rolling(self.kc_length).mean()

        ema = data["Close"].ewm(span=self.kc_length).mean()

        upper_kc = ema + atr * self.kc_mult
        lower_kc = ema - atr * self.kc_mult

        bb_upper = bb.iloc[:, 2]
        bb_lower = bb.iloc[:, 0]

        squeeze_on = (
            (bb_lower > lower_kc)
            &
            (bb_upper < upper_kc)
        )

        squeeze_off = (
            (bb_lower < lower_kc)
            &
            (bb_upper > upper_kc)
        )

        width = (
            (bb_upper - bb_lower)
            /
            bb.iloc[:, 1]
        ) * 100

        data["BB_Width"] = width
        data["KC_Upper"] = upper_kc
        data["KC_Lower"] = lower_kc

        data["Squeeze_ON"] = squeeze_on
        data["Squeeze_OFF"] = squeeze_off

        return data

    def latest_signal(self, df):

        d = self.calculate(df)

        last = d.iloc[-1]

        score = 0

        if last["Squeeze_ON"]:
            score += 40

        if last["BB_Width"] < 6:
            score += 30

        if last["BB_Width"] < 4:
            score += 20

        probability = min(score, 100)

        return {
            "squeeze": bool(last["Squeeze_ON"]),
            "released": bool(last["Squeeze_OFF"]),
            "bb_width": round(float(last["BB_Width"]), 2),
            "probability": probability
        }


if __name__ == "__main__":

    import yfinance as yf

    df = yf.download(
        "NVDA",
        period="6mo",
        progress=False
    )

    detector = SqueezeDetector()

    result = detector.latest_signal(df)

    print(result)
