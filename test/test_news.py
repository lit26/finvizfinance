"""Offline fixture tests for the news scraper (see test_quote for the pattern)."""

import pytest

from finvizfinance.news import News
from finvizfinance.exceptions import FinvizParseError, FinvizBlockedError

from conftest import use_session, html_response, blocked_response


def test_news_real():
    use_session(html_response("news.html"))
    all_news = News().get_news()
    news = all_news["news"]
    blogs = all_news["blogs"]
    assert len(news) == 2
    assert len(blogs) == 1
    assert news.iloc[0]["Title"] == "Market rallies on data"
    assert news.iloc[0]["Source"] == "www.reuters.com"


def test_news_drift_raises_parse_error():
    use_session(html_response("news_drift.html"))
    with pytest.raises(FinvizParseError):
        News().get_news()


def test_news_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        News()
