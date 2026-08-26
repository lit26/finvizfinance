"""Offline fixture tests for the screener views (see test_quote for the pattern)."""

import pytest

from finvizfinance.screener.overview import Overview
from finvizfinance.screener.ticker import Ticker
from finvizfinance.screener import get_signal, get_filters, get_filter_options
from finvizfinance.exceptions import FinvizParseError, FinvizBlockedError

from conftest import use_session, html_response, blocked_response


def test_screener_overview_real():
    use_session(html_response("screener_overview.html"))
    df = Overview().screener_view(verbose=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT"]


def test_screener_overview_multipage():
    use_session(
        [
            html_response("screener_multi_p1.html"),
            html_response("screener_multi_p2.html"),
        ]
    )
    df = Overview().screener_view(verbose=0, sleep_sec=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT", "GOOGL"]


def test_screener_drift_raises_parse_error():
    use_session(html_response("screener_drift.html"))
    with pytest.raises(FinvizParseError):
        Overview().screener_view(verbose=0)


def test_screener_no_results_returns_none():
    use_session(html_response("screener_noresults.html"))
    assert Overview().screener_view(verbose=0) is None


def test_screener_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Overview().screener_view(verbose=0)


def test_screener_ticker_view():
    use_session(html_response("screener_ticker.html"))
    tickers = Ticker().screener_view(verbose=0)
    assert tickers == ["AAPL", "MSFT"]


def test_screener_ticker_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Ticker().screener_view(verbose=0)


def test_screener_get_settings():
    assert isinstance(get_signal(), list)
    assert isinstance(get_filters(), list)
    assert isinstance(get_filter_options("Exchange"), list)
    with pytest.raises(ValueError):
        get_filter_options("Dummy")
