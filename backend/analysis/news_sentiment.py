"""
ByToBy Pro v3
News Sentiment Analysis Engine

Analyze financial news sentiment using FinBERT or Transformers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from transformers import pipeline


@dataclass
class NewsItem:

    title: str
    summary: str = ""


class NewsSentimentEngine:

    def __init__(self):

        self.classifier = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert"
        )

    # ---------------------------------------------------------

    def analyze_article(self, text: str):

        result = self.classifier(text[:512])[0]

        label = result["label"]

        confidence = float(result["score"])

        if label.upper() == "POSITIVE":
            score = 100

        elif label.upper() == "NEGATIVE":
            score = 0

        else:
            score = 50

        return {

            "label": label,

            "score": score,

            "confidence": round(confidence * 100, 2)

        }

    # ---------------------------------------------------------

    def analyze_news(self, news: List[dict]):

        if not news:

            return {

                "score": 50,

                "label": "Neutral",

                "confidence": 0,

                "articles": []

            }

        scores = []

        articles = []

        for item in news:

            text = item.get("title", "")

            summary = item.get("summary", "")

            result = self.analyze_article(

                f"{text}. {summary}"

            )

            scores.append(result["score"])

            articles.append({

                "title": text,

                "label": result["label"],

                "confidence": result["confidence"],

                "score": result["score"]

            })

        avg = sum(scores) / len(scores)

        if avg >= 70:

            label = "Bullish"

        elif avg >= 55:

            label = "Positive"

        elif avg >= 45:

            label = "Neutral"

        elif avg >= 30:

            label = "Negative"

        else:

            label = "Bearish"

        return {

            "score": round(avg),

            "label": label,

            "confidence": round(

                sum(a["confidence"] for a in articles)

                / len(articles),

                2

            ),

            "articles": articles

        }


if __name__ == "__main__":

    sample_news = [

        {

            "title": "NVIDIA beats earnings expectations",

            "summary": "Revenue increased more than analysts expected."

        },

        {

            "title": "Major institutions continue buying shares",

            "summary": "Several funds increased their positions."

        }

    ]

    engine = NewsSentimentEngine()

    result = engine.analyze_news(sample_news)

    from pprint import pprint

    pprint(result)
