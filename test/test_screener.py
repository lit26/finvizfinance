"""Offline fixture tests for the screener views (see test_quote for the pattern)."""

import pytest

from finvizfinance.screener.overview import Overview
from finvizfinance.screener.ticker import Ticker
from finvizfinance.screener.custom import Custom
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


def test_screener_ticker_not_doubled():
    # Regression (#159): finviz nests two anchors in the ticker cell (a
    # logo/company-ticker link + a tab-link), so the cell's text repeats the
    # symbol ("AAPL" -> "AAPLAAPL"). The parser must read the clean value from
    # the ``data-boxover-ticker`` attribute, without disturbing other columns.
    use_session(html_response("screener_overview.html"))
    df = Overview().screener_view(verbose=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT"]
    assert list(df["Company"]) == ["Apple Inc.", "Microsoft"]


def test_screener_duplicate_headers_preserved_across_pages():
    # Regression (#150): a wide custom view can return duplicate header labels
    # (finviz renders two "Dividend" columns). The old name-keyed dict collapsed
    # them, silently shrinking page 1 to a single "Dividend" and then raising
    # ``IndexError`` while parsing page 2, once the cell count exceeded the
    # now-shorter header list.
    use_session(
        [
            html_response("screener_custom_dupcols_p1.html"),
            html_response("screener_custom_dupcols_p2.html"),
        ]
    )
    df = Custom().screener_view(limit=100000, verbose=0, sleep_sec=0)
    # Both "Dividend" columns survive (pandas allows duplicate labels)...
    assert list(df.columns) == ["Ticker", "Dividend", "Sector", "Dividend"]
    # ...all three rows across both pages parsed (no IndexError, no collapse)...
    assert len(df) == 3
    assert list(df.iloc[:, 0]) == ["AAPL", "MSFT", "GOOGL"]
    assert list(df.iloc[:, 2]) == [
        "Technology",
        "Technology",
        "Communication Services",
    ]
    # ...and the two "Dividend" columns hold distinct values (not collapsed).
    assert df.iloc[0, 1] != df.iloc[0, 3]


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
