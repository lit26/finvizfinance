"""Offline fixture tests for the screener views (see test_quote for the pattern)."""

import pandas as pd
import pytest
from conftest import blocked_response, html_response, use_session

from finvizfinance.exceptions import FinvizBlockedError, FinvizParseError
from finvizfinance.screener import get_filter_options, get_filters, get_signal
from finvizfinance.screener.custom import Custom
from finvizfinance.screener.financial import Financial
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.ownership import Ownership
from finvizfinance.screener.performance import Performance
from finvizfinance.screener.technical import Technical
from finvizfinance.screener.ticker import Ticker
from finvizfinance.screener.util import get_custom_screener_columns, get_orders
from finvizfinance.screener.valuation import Valuation


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
    # Regression (#159): the ticker cell's text repeats the symbol (logo +
    # link: "AAPL" -> "AAPLAAPL"). The parser must read the clean value from
    # the embedded JSON rows, without disturbing other columns.
    use_session(html_response("screener_overview.html"))
    df = Overview().screener_view(verbose=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT"]
    assert list(df["Company"]) == ["Apple Inc.", "Microsoft"]


def test_screener_duplicate_headers_preserved_across_pages():
    # Regression (#150): a wide custom view can return duplicate header labels
    # (Dividend Yield and Dividend are both "Dividend"). A name-keyed dict
    # collapsed them, silently shrinking the frame. The fixture's grid only
    # renders the first columns (finviz virtualizes wide views), so the
    # columns must come from the requested indexes, not the DOM.
    use_session(
        [
            html_response("screener_custom_dupcols_p1.html"),
            html_response("screener_custom_dupcols_p2.html"),
        ]
    )
    df = Custom().screener_view(
        limit=100000, verbose=0, sleep_sec=0, columns=[1, 14, 3, 75]
    )
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


def test_screener_values_match_legacy_table():
    # The JSON carries raw values; they are converted to what the legacy
    # table's text cells parsed to ("3.00T" -> 3e12, "0.45%" -> 0.0045).
    use_session(html_response("screener_values.html"))
    df = Overview().screener_view(verbose=0)
    assert list(df.columns) == [
        "Ticker",
        "Market Cap",
        "Fwd P/E",
        "Dividend",
        "Volume",
        "Earnings",
        "IPO Date",
        "Index",
    ]
    aapl, newco = df.iloc[0], df.iloc[1]
    assert aapl["Market Cap"] == pytest.approx(3000000.5e6)
    assert aapl["Fwd P/E"] == pytest.approx(28.5)
    assert aapl["Dividend"] == pytest.approx(0.0045)
    assert aapl["Volume"] == 52000000.0
    assert aapl["Earnings"] == "May 02/a"
    assert aapl["IPO Date"] == "12/12/1980"
    assert aapl["Index"] == "DJIA, S&P 500"
    # No session time -> no before/after suffix; absent values are missing.
    assert newco["Earnings"] == "May 03"
    assert pd.isna(newco["Fwd P/E"])
    assert pd.isna(newco["IPO Date"])


@pytest.mark.parametrize("fixture", ["screener_drift.html", "screener_drift_json.html"])
def test_screener_drift_raises_parse_error(fixture):
    use_session(html_response(fixture))
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


@pytest.mark.parametrize(
    "view_cls", [Financial, Ownership, Performance, Technical, Valuation]
)
def test_screener_views_parse_table(view_cls):
    # Each screener view inherits Base.screener_view; exercise them all.
    use_session(html_response("screener_overview.html"))
    df = view_cls().screener_view(verbose=0)
    assert list(df["Ticker"]) == ["AAPL", "MSFT"]


def test_screener_etf_overview_columns():
    # An ETF-filtered request is served by finviz's ETF screener, whose
    # e.-prefixed column ids map to readable DataFrame columns.
    use_session(html_response("screener_etf_overview.html"))
    df = Overview().screener_view(verbose=0)
    assert list(df.columns) == [
        "Ticker",
        "Company",
        "Category",
        "Tags",
        "Dividend",
        "Price",
        "Change",
    ]
    assert list(df["Category"]) == ["U.S. Equity - Large Cap", "Bonds - Broad Market"]
    assert df["Dividend"].iloc[0] == pytest.approx(0.012)


@pytest.mark.parametrize("view_cls", [Financial, Ownership, Valuation])
def test_screener_stock_only_view_warns_on_etf_fallback(view_cls):
    # The ETF screener has no Valuation/Financial/Ownership view; finviz
    # answers with its ETF overview columns, which must not pass silently.
    use_session(html_response("screener_etf_overview.html"))
    with pytest.warns(UserWarning, match="ETF screener has no"):
        df = view_cls().screener_view(verbose=0)
    assert "Category" in df.columns


@pytest.mark.parametrize("view_cls", [Overview, Performance, Technical])
def test_screener_etf_capable_view_does_not_warn(view_cls, recwarn):
    use_session(html_response("screener_etf_overview.html"))
    view_cls().screener_view(verbose=0)
    assert not [w for w in recwarn if "ETF screener" in str(w.message)]


def test_screener_etf_filters():
    view = Overview()
    view.set_filter(
        filters_dict={
            "Industry": "Exchange Traded Fund",
            "Single Category": "Bonds - Broad Market",
            "Net Expense Ratio": "Under 0.1%",
            "Net Fund Flows": "1 Month - Over 0%",
        }
    )
    assert view.request_params["f"] == (
        "ind_exchangetradedfund,etf_category_bondsbroadmarket,"
        "etf_netexpense_u01,etf_fundflows_1mo0"
    )


def test_screener_custom_parse_columns_prepends_zero():
    view = Custom()
    view._parse_columns([2, 1])
    assert view.request_params["c"] == "0,2,1"


def test_screener_custom_parse_columns_dedupes_leading_zero():
    view = Custom()
    view._parse_columns([0, 5])
    assert view.request_params["c"] == "0,5"


def test_screener_custom_parse_columns_empty_is_noop():
    view = Custom()
    view._parse_columns([])
    assert "c" not in view.request_params


def test_screener_util_get_orders_and_columns():
    assert isinstance(get_orders(), list) and len(get_orders()) > 0
    columns = get_custom_screener_columns()
    assert isinstance(columns, dict) and len(columns) > 0
