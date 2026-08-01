"""
ByToBy Pro v3
Pattern Detection Engine

Detects chart patterns used by AI Scanner.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


class PatternDetector:

    def __init__(self, df: pd.DataFrame):

        self.df = df.copy()

    # ---------------------------------------------------------

    def double_bottom(self, lookback=40):

        low = self.df["low"].tail(lookback)

        first = low.idxmin()

        second = low[first + 5 :].idxmin()

        price1 = low.loc[first]
        price2 = low.loc[second]

        diff = abs(price1 - price2) / price1

        return diff < 0.03

    # ---------------------------------------------------------

    def double_top(self, lookback=40):

        high = self.df["high"].tail(lookback)

        first = high.idxmax()

        second = high[first + 5 :].idxmax()

        price1 = high.loc[first]
        price2 = high.loc[second]

        diff = abs(price1 - price2) / price1

        return diff < 0.03

    # ---------------------------------------------------------

    def higher_highs(self):

        high = self.df["high"].tail(5).values

        return all(

            high[i] > high[i - 1]

            for i in range(1, len(high))

        )

    # ---------------------------------------------------------

    def higher_lows(self):

        low = self.df["low"].tail(5).values

        return all(

            low[i] > low[i - 1]

            for i in range(1, len(low))

        )

    # ---------------------------------------------------------

    def lower_highs(self):

        high = self.df["high"].tail(5).values

        return all(

            high[i] < high[i - 1]

            for i in range(1, len(high))

        )

    # ---------------------------------------------------------

    def lower_lows(self):

        low = self.df["low"].tail(5).values

        return all(

            low[i] < low[i - 1]

            for i in range(1, len(low))

        )

    # ---------------------------------------------------------

    def ascending_triangle(self):

        resistance = self.df["high"].tail(20).max()

        highs = self.df["high"].tail(20)

        lows = self.df["low"].tail(20)

        flat = (

            abs(highs.mean() - resistance)

            / resistance

        ) < 0.02

        rising = lows.iloc[-1] > lows.iloc[0]

        return flat and rising

    # ---------------------------------------------------------

    def descending_triangle(self):

        support = self.df["low"].tail(20).min()

        highs = self.df["high"].tail(20)

        lows = self.df["low"].tail(20)

        flat = (

            abs(lows.mean() - support)

            / support

        ) < 0.02

        falling = highs.iloc[-1] < highs.iloc[0]

        return flat and falling

    # ---------------------------------------------------------

    def bull_flag(self):

        close = self.df["close"]

        recent = close.tail(25)

        impulse = (

            recent.iloc[10] -

            recent.iloc[0]

        ) / recent.iloc[0]

        consolidation = (

            recent.tail(10).max()

            -

            recent.tail(10).min()

        ) / recent.tail(10).mean()

        return (

            impulse > 0.15

            and

            consolidation < 0.05

        )

    # ---------------------------------------------------------

    def bear_flag(self):

        close = self.df["close"]

        recent = close.tail(25)

        drop = (

            recent.iloc[0]

            -

            recent.iloc[10]

        ) / recent.iloc[0]

        consolidation = (

            recent.tail(10).max()

            -

            recent.tail(10).min()

        ) / recent.tail(10).mean()

        return (

            drop > 0.15

            and

            consolidation < 0.05

        )

    # ---------------------------------------------------------

    def channel(self):

        high = self.df["high"].tail(30)

        low = self.df["low"].tail(30)

        slope_high = np.polyfit(

            range(len(high)),

            high,

            1

        )[0]

        slope_low = np.polyfit(

            range(len(low)),

            low,

            1

        )[0]

        return abs(

            slope_high -

            slope_low

        ) < 0.1

    # ---------------------------------------------------------

    def wedge(self):

        high = self.df["high"].tail(25)

        low = self.df["low"].tail(25)

        range_start = high.iloc[0] - low.iloc[0]

        range_end = high.iloc[-1] - low.iloc[-1]

        return range_end < range_start * 0.6

    # ---------------------------------------------------------

    def analyze(self):

        patterns = {

            "double_bottom": self.double_bottom(),

            "double_top": self.double_top(),

            "higher_highs": self.higher_highs(),

            "higher_lows": self.higher_lows(),

            "lower_highs": self.lower_highs(),

            "lower_lows": self.lower_lows(),

            "ascending_triangle":
                self.ascending_triangle(),

            "descending_triangle":
                self.descending_triangle(),

            "bull_flag":
                self.bull_flag(),

            "bear_flag":
                self.bear_flag(),

            "channel":
                self.channel(),

            "wedge":
                self.wedge()

        }

        score = 0

        bullish = [

            "double_bottom",

            "higher_highs",

            "higher_lows",

            "ascending_triangle",

            "bull_flag"

        ]

        for name in bullish:

            if patterns[name]:

                score += 20

        score = min(score, 100)

        return {

            "patterns": patterns,

            "pattern_score": score

        }


if __name__ == "__main__":

    from backend.data_providers.market_data import market_data

    df = market_data.history("NVDA")

    detector = PatternDetector(df)

    result = detector.analyze()

    print(result)
