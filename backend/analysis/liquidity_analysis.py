"""
ByToBy Pro v3
Liquidity & Smart Money Analysis Engine

Author: ByToBy
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class LiquidityAnalysis:

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    # ---------------------------------------------------------
    # Relative Volume
    # ---------------------------------------------------------

    def relative_volume(self):

        self.df["VOL20"] = (
            self.df["volume"]
            .rolling(20)
            .mean()
        )

        self.df["RVOL"] = (
            self.df["volume"]
            /
            self.df["VOL20"]
        )

    # ---------------------------------------------------------
    # VWAP
    # ---------------------------------------------------------

    def vwap(self):

        typical = (
            self.df["high"] +
            self.df["low"] +
            self.df["close"]
        ) / 3

        cumulative_price = (
            typical * self.df["volume"]
        ).cumsum()

        cumulative_volume = (
            self.df["volume"]
        ).cumsum()

        self.df["VWAP"] = (
            cumulative_price /
            cumulative_volume
        )

    # ---------------------------------------------------------
    # OBV
    # ---------------------------------------------------------

    def obv(self):

        obv = [0]

        close = self.df["close"].values
        volume = self.df["volume"].values

        for i in range(1, len(close)):

            if close[i] > close[i - 1]:
                obv.append(obv[-1] + volume[i])

            elif close[i] < close[i - 1]:
                obv.append(obv[-1] - volume[i])

            else:
                obv.append(obv[-1])

        self.df["OBV"] = obv

    # ---------------------------------------------------------
    # CMF
    # ---------------------------------------------------------

    def cmf(self, period=20):

        multiplier = (
            (
                (self.df["close"] - self.df["low"])
                -
                (self.df["high"] - self.df["close"])
            )
            /
            (
                self.df["high"] - self.df["low"]
            )
            .replace(0, np.nan)
        )

        mfv = multiplier * self.df["volume"]

        self.df["CMF"] = (
            mfv.rolling(period).sum()
            /
            self.df["volume"].rolling(period).sum()
        )

    # ---------------------------------------------------------
    # Money Flow Index
    # ---------------------------------------------------------

    def mfi(self, period=14):

        tp = (
            self.df["high"] +
            self.df["low"] +
            self.df["close"]
        ) / 3

        mf = tp * self.df["volume"]

        positive = [0]
        negative = [0]

        for i in range(1, len(tp)):

            if tp.iloc[i] > tp.iloc[i - 1]:
                positive.append(mf.iloc[i])
                negative.append(0)

            else:
                positive.append(0)
                negative.append(mf.iloc[i])

        positive = pd.Series(positive)
        negative = pd.Series(negative)

        pos = positive.rolling(period).sum()
        neg = negative.rolling(period).sum()

        ratio = pos / neg.replace(0, np.nan)

        self.df["MFI"] = (
            100 -
            (
                100 /
                (1 + ratio)
            )
        )

    # ---------------------------------------------------------
    # Accumulation Score
    # ---------------------------------------------------------

    def accumulation_score(self):

        score = 0

        last = self.df.iloc[-1]

        if last["RVOL"] > 2:
            score += 20

        elif last["RVOL"] > 1.5:
            score += 10

        if last["CMF"] > 0.20:
            score += 20

        elif last["CMF"] > 0:
            score += 10

        if last["MFI"] > 60:
            score += 20

        if last["close"] > last["VWAP"]:
            score += 20

        if (
            self.df["OBV"].iloc[-1]
            >
            self.df["OBV"].iloc[-5]
        ):
            score += 20

        return min(score, 100)

    # ---------------------------------------------------------
    # Smart Money
    # ---------------------------------------------------------

    def smart_money_signal(self):

        score = self.accumulation_score()

        if score >= 80:
            return "Strong Accumulation"

        if score >= 60:
            return "Accumulation"

        if score >= 40:
            return "Neutral"

        if score >= 20:
            return "Distribution"

        return "Strong Distribution"

    # ---------------------------------------------------------
    # Main
    # ---------------------------------------------------------

    def analyze(self):

        self.relative_volume()

        self.vwap()

        self.obv()

        self.cmf()

        self.mfi()

        last = self.df.iloc[-1]

        return {

            "relative_volume":
                round(last["RVOL"], 2),

            "vwap":
                round(last["VWAP"], 2),

            "cmf":
                round(last["CMF"], 3),

            "mfi":
                round(last["MFI"], 2),

            "obv":
                int(last["OBV"]),

            "smart_money":
                self.smart_money_signal(),

            "accumulation_score":
                self.accumulation_score(),

            "data":
                self.df
        }


if __name__ == "__main__":

    from backend.data_providers.market_data import market_data

    df = market_data.history("PLTR")

    analyzer = LiquidityAnalysis(df)

    result = analyzer.analyze()

    print(result)
