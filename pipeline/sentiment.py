"""Sentiment analysis using VADER (on English-translated text)."""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text):
    """Analyze sentiment of English text. Returns (score, label).

    score: compound score from -1 (most negative) to +1 (most positive)
    label: 'positive', 'negative', or 'neutral'
    """
    if not text or not text.strip():
        return 0.0, "neutral"
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return round(compound, 3), label
