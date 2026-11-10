"""Offline fixture tests for the future scraper."""

import pytest
from conftest import blocked_response, html_response, use_session

from finvizfinance.exceptions import FinvizBlockedError, FinvizParseError
from finvizfinance.future import Future


def test_future_real():
    use_session(html_response("futures.html"))
    df = Future().performance()
    assert not df.empty
    assert list(df["ticker"]) == ["ES", "NQ"]


def test_future_current_client_rendered_format():
    use_session(html_response("futures_current.html"))
    df = Future().performance()
    assert list(df["ticker"]) == ["ES", "NQ"]
    assert list(df["perf"])[0]["day"] == 0.5


def test_future_timeframe_param():
    fake = use_session(html_response("futures.html"))
    Future().performance(timeframe="W")
    assert fake.calls[0]["params"] == {"v": 12}


def test_future_drift_raises_parse_error():
    use_session(html_response("futures_drift.html"))
    with pytest.raises(FinvizParseError):
        Future().performance()


def test_future_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Future().performance()


def test_future_invalid_timeframe():
    with pytest.raises(ValueError):
        Future().performance(timeframe="dummy")


def test_future_perf_init_json():
    # Redesigned page (#185): rows ship as JSON in script#futures-perf-init-data.
    use_session(html_response("futures_perf_init.html"))
    df = Future().performance()
    assert df["ticker"][0] == "10Y"
    assert "perfDayPct" in df.columns
