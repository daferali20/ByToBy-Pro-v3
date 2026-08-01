"""
ByToBy Pro v3
Fundamental Analysis Engine

Fundamental Score (0-100)
Fair Value Estimation
"""

from __future__ import annotations

import math
import yfinance as yf


class FundamentalAnalysis:

    def __init__(self, symbol: str):

        self.symbol = symbol.upper()

        self.ticker = yf.Ticker(self.symbol)

        self.info = self.ticker.info

    # -----------------------------------------------------

    def _get(self, key, default=0):

        value = self.info.get(key)

        if value is None:

            return default

        return value

    # -----------------------------------------------------

    def valuation(self):

        return {

            "market_cap": self._get("marketCap"),

            "enterprise_value": self._get("enterpriseValue"),

            "trailing_pe": self._get("trailingPE"),

            "forward_pe": self._get("forwardPE"),

            "peg": self._get("pegRatio"),

            "price_to_book": self._get("priceToBook"),

            "price_to_sales": self._get("priceToSalesTrailing12Months")

        }

    # -----------------------------------------------------

    def profitability(self):

        return {

            "roe": self._get("returnOnEquity"),

            "roa": self._get("returnOnAssets"),

            "profit_margin": self._get("profitMargins"),

            "operating_margin": self._get("operatingMargins"),

            "gross_margin": self._get("grossMargins")

        }

    # -----------------------------------------------------

    def growth(self):

        return {

            "earnings_growth": self._get("earningsGrowth"),

            "revenue_growth": self._get("revenueGrowth"),

            "eps_forward": self._get("forwardEps"),

            "eps_trailing": self._get("trailingEps")

        }

    # -----------------------------------------------------

    def financial_health(self):

        return {

            "current_ratio": self._get("currentRatio"),

            "quick_ratio": self._get("quickRatio"),

            "debt_to_equity": self._get("debtToEquity"),

            "free_cash_flow": self._get("freeCashflow"),

            "operating_cash_flow": self._get("operatingCashflow")

        }

    # -----------------------------------------------------

    def fair_value(self):

        price = self._get("currentPrice")

        forward_pe = self._get("forwardPE")

        eps = self._get("forwardEps")

        if not forward_pe:

            return price

        if not eps:

            return price

        industry_pe = max(forward_pe, 20)

        value = eps * industry_pe

        return round(value, 2)

    # -----------------------------------------------------

    def undervaluation(self):

        current = self._get("currentPrice")

        fair = self.fair_value()

        if current == 0:

            return 0

        return round(

            ((fair - current) / current) * 100,

            2

        )

    # -----------------------------------------------------

    def score(self):

        score = 0

        pe = self._get("forwardPE")

        peg = self._get("pegRatio")

        roe = self._get("returnOnEquity")

        growth = self._get("revenueGrowth")

        margin = self._get("profitMargins")

        debt = self._get("debtToEquity")

        if pe and pe < 30:
            score += 15

        if peg and peg < 2:
            score += 15

        if roe and roe > 0.15:
            score += 15

        if growth and growth > 0.15:
            score += 15

        if margin and margin > 0.15:
            score += 15

        if debt and debt < 80:
            score += 15

        if self.undervaluation() > 15:
            score += 10

        return min(score, 100)

    # -----------------------------------------------------

    def recommendation(self):

        s = self.score()

        if s >= 90:
            return "Strong Buy"

        if s >= 75:
            return "Buy"

        if s >= 60:
            return "Watch"

        if s >= 40:
            return "Neutral"

        return "Weak"

    # -----------------------------------------------------

    def analyze(self):

        return {

            "symbol": self.symbol,

            "company": self._get("longName"),

            "sector": self._get("sector"),

            "industry": self._get("industry"),

            "valuation": self.valuation(),

            "growth": self.growth(),

            "profitability": self.profitability(),

            "financial_health": self.financial_health(),

            "fair_value": self.fair_value(),

            "undervaluation_percent": self.undervaluation(),

            "fundamental_score": self.score(),

            "recommendation": self.recommendation()

        }


if __name__ == "__main__":

    engine = FundamentalAnalysis("NVDA")

    result = engine.analyze()

    from pprint import pprint

    pprint(result)
