"""
ByToBy Pro v3
Market Data Provider

Unified market data interface.

Author: ByToBy
"""

from __future__ import annotations

from datetime import datetime
from functools import lru_cache

import pandas as pd
import yfinance as yf


class MarketDataProvider:
    """
    Unified provider for market data.
    """

    def __init__(self):
        self.default_period = "1y"
        self.default_interval = "1d"

    # ---------------------------------------------------------
    # Historical Data
    # ---------------------------------------------------------

    def history(
        self,
        symbol: str,
        period: str | None = None,
        interval: str | None = None,
    ) -> pd.DataFrame:

        period = period or self.default_period
        interval = interval or self.default_interval

        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
            threads=False,
        )

        if df.empty:
            raise ValueError(f"No data returned for {symbol}")

        df.reset_index(inplace=True)

        rename = {
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
            "Date": "date",
            "Datetime": "date",
        }

        df.rename(columns=rename, inplace=True)

        return df

    # ---------------------------------------------------------
    # Quote
    # ---------------------------------------------------------

    @lru_cache(maxsize=512)
    def quote(self, symbol: str):

        ticker = yf.Ticker(symbol)

        info = ticker.fast_info

        return {
            "symbol": symbol.upper(),
            "price": info.get("lastPrice"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "open": info.get("open"),
            "previous_close": info.get("previousClose"),
            "volume": info.get("lastVolume"),
            "market_cap": info.get("marketCap"),
            "currency": info.get("currency"),
        }

    # ---------------------------------------------------------
    # Company
    # ---------------------------------------------------------

    @lru_cache(maxsize=256)
    def company(self, symbol: str):

        ticker = yf.Ticker(symbol)

        info = ticker.info

        return {
            "symbol": symbol.upper(),
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "website": info.get("website"),
            "employees": info.get("fullTimeEmployees"),
            "summary": info.get("longBusinessSummary"),
        }

    # ---------------------------------------------------------
    # Financials
    # ---------------------------------------------------------

    def financials(self, symbol: str):

        ticker = yf.Ticker(symbol)

        return {
            "income_statement": ticker.financials,
            "balance_sheet": ticker.balance_sheet,
            "cashflow": ticker.cashflow,
        }

    # ---------------------------------------------------------
    # News
    # ---------------------------------------------------------

    def news(self, symbol: str):

        ticker = yf.Ticker(symbol)

        news = ticker.news

        items = []

        for item in news:

            items.append(
                {
                    "title": item.get("title"),
                    "publisher": item.get("publisher"),
                    "link": item.get("link"),
                    "published": datetime.fromtimestamp(
                        item.get("providerPublishTime", 0)
                    ),
                }
            )

        return items

    # ---------------------------------------------------------
    # Multiple Symbols
    # ---------------------------------------------------------

    def batch_history(
        self,
        symbols: list[str],
        period="6mo",
        interval="1d",
    ):

        result = {}

        for symbol in symbols:

            try:
                result[symbol] = self.history(
                    symbol,
                    period,
                    interval,
                )
            except Exception:
                continue

        return result


market_data = MarketDataProvider()


if __name__ == "__main__":

    provider = MarketDataProvider()

    print(provider.quote("NVDA"))

    df = provider.history("AAPL")

    print(df.tail())
