"""
ByToBy Pro v3
AI Scoring Engine

Combines all analysis engines into one AI Score.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AIResult:

    ai_score: int

    confidence: int

    recommendation: str

    explosion_probability: int

    risk: str

    summary: str


class AIScoreEngine:

    def __init__(
        self,
        technical,
        liquidity,
        fundamental,
        patterns,
        squeeze=None,
        sentiment=None,
    ):

        self.technical = technical
        self.liquidity = liquidity
        self.fundamental = fundamental
        self.patterns = patterns
        self.squeeze = squeeze or {}
        self.sentiment = sentiment or {}

    # --------------------------------------------------------

    def score_technical(self):

        score = 0

        if self.technical["trend"] == "Bullish":
            score += 10

        if self.technical["golden_cross"]:
            score += 10

        if 45 <= self.technical["rsi"] <= 70:
            score += 10

        if self.technical["relative_volume"] >= 2:
            score += 10

        if self.technical["bb_width"] < 6:
            score += 10

        return min(score, 50)

    # --------------------------------------------------------

    def score_liquidity(self):

        score = self.liquidity["accumulation_score"]

        return min(score, 100)

    # --------------------------------------------------------

    def score_fundamental(self):

        return self.fundamental["fundamental_score"]

    # --------------------------------------------------------

    def score_patterns(self):

        return self.patterns["pattern_score"]

    # --------------------------------------------------------

    def score_squeeze(self):

        if not self.squeeze:

            return 0

        return self.squeeze.get("probability", 0)

    # --------------------------------------------------------

    def score_sentiment(self):

        if not self.sentiment:

            return 50

        return self.sentiment.get("score", 50)

    # --------------------------------------------------------

    def calculate(self):

        tech = self.score_technical()

        fund = self.score_fundamental()

        liquidity = self.score_liquidity()

        patterns = self.score_patterns()

        squeeze = self.score_squeeze()

        sentiment = self.score_sentiment()

        ai = (

            tech * 0.20 +

            fund * 0.20 +

            liquidity * 0.20 +

            patterns * 0.15 +

            squeeze * 0.15 +

            sentiment * 0.10

        )

        ai = round(ai)

        confidence = min(

            100,

            round(

                (tech +

                 liquidity +

                 patterns +

                 squeeze)

                / 4

            )

        )

        explosion = round(

            (

                squeeze * 0.40 +

                liquidity * 0.30 +

                patterns * 0.20 +

                tech * 0.10

            )

        )

        if ai >= 90:

            recommendation = "Strong Buy"

            risk = "Very Low"

        elif ai >= 80:

            recommendation = "Buy"

            risk = "Low"

        elif ai >= 70:

            recommendation = "Watch"

            risk = "Medium"

        elif ai >= 60:

            recommendation = "Neutral"

            risk = "Medium"

        else:

            recommendation = "Avoid"

            risk = "High"

        summary = self.build_summary(

            ai,

            explosion,

            recommendation,

        )

        return AIResult(

            ai_score=ai,

            confidence=confidence,

            recommendation=recommendation,

            explosion_probability=explosion,

            risk=risk,

            summary=summary,

        )

    # --------------------------------------------------------

    def build_summary(

        self,

        ai,

        explosion,

        recommendation,

    ):

        text = []

        text.append(

            f"AI Score: {ai}/100"

        )

        text.append(

            f"Explosion Probability: {explosion}%"

        )

        text.append(

            f"Recommendation: {recommendation}"

        )

        if explosion >= 85:

            text.append(

                "Strong squeeze with institutional accumulation detected."

            )

        elif explosion >= 70:

            text.append(

                "High probability breakout candidate."

            )

        elif explosion >= 50:

            text.append(

                "Monitor closely."

            )

        else:

            text.append(

                "No significant breakout signal."

            )

        return " | ".join(text)
