"""Offline fixture tests for the quote scrapers.

This module is the exemplar the other scraper test modules copy: each scraper
is exercised through the injected-session seam against saved HTML, covering the
four canonical cases — real 200, Drifted fixture, Cloudflare Wall, and a
missing optional field.
"""

import pytest

from finvizfinance.quote import finvizfinance, Statements
from finvizfinance.exceptions import FinvizParseError, FinvizBlockedError

from conftest import use_session, html_response, blocked_response, FakeResponse


def _stock(fixture):
    """Build a finvizfinance bound to a saved quote fixture."""
    use_session(html_response(fixture))
    return finvizfinance("AAPL")


# --- ticker_fundament: the four canonical cases -----------------------------


def test_fundament_real():
    fundament = _stock("quote_aapl.html").ticker_fundament()
    assert fundament["Company"] == "Apple Inc."
    assert fundament["Sector"] == "Technology"
    assert fundament["Industry"] == "Consumer Electronics"
    assert fundament["Country"] == "USA"
    assert fundament["Exchange"] == "NASDAQ"
    assert fundament["P/E"] == "25.50"
    assert fundament["Market Cap"] == "3050.00B"
    assert fundament["52W Range From"] == "164.08"
    assert fundament["52W Range To"] == "260.10"
    assert fundament["Volatility W"] == "1.50%"
    assert fundament["Volatility M"] == "2.00%"
    assert fundament["Optionable"] == "Yes"
    assert fundament["EPS next Y"] == "7.50"
    assert fundament["EPS next Y Percentage"] == "8.20%"


def test_fundament_drift_raises_parse_error():
    stock = _stock("quote_drift.html")
    with pytest.raises(FinvizParseError) as exc:
        stock.ticker_fundament()
    assert exc.value.selector == "table.snapshot-table2"


def test_fundament_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        finvizfinance("AAPL")


def test_fundament_missing_optional_classification_warns():
    stock = _stock("quote_etf.html")
    with pytest.warns(UserWarning):
        fundament = stock.ticker_fundament()
    assert fundament["Company"] == "SPDR S&P 500 ETF Trust"
    assert fundament["Sector"] is None
    assert fundament["Industry"] is None
    assert fundament["Country"] is None
    assert fundament["Exchange"] is None


def test_fundament_renamed_links_recovered_via_fallback():
    # Drift: the quote-links div was renamed; the guard falls back to the
    # stable screener-filter anchors and still resolves the classification.
    fundament = _stock("quote_renamed_links.html").ticker_fundament()
    assert fundament["Sector"] == "Technology"
    assert fundament["Industry"] == "Consumer Electronics"
    assert fundament["Country"] == "USA"
    assert fundament["Exchange"] == "NASDAQ"


def test_fundament_series_output_format():
    df = _stock("quote_aapl.html").ticker_fundament(output_format="series")
    assert df.loc["Company", "Stat"] == "Apple Inc."


# --- other quote methods (ticket 06) ----------------------------------------


def test_ticker_description():
    desc = _stock("quote_aapl.html").ticker_description()
    assert "designs, manufactures" in desc


def test_ticker_peer():
    assert _stock("quote_aapl.html").ticker_peer() == ["MSFT", "GOOGL", "AMZN"]


def test_ticker_etf_holders():
    assert _stock("quote_aapl.html").ticker_etf_holders() == ["SPY", "QQQ", "VOO"]


def test_ticker_peer_absent_returns_empty_and_warns():
    stock = _stock("quote_etf.html")
    with pytest.warns(UserWarning):
        assert stock.ticker_peer() == []


def test_ticker_outer_ratings():
    df = _stock("quote_aapl.html").ticker_outer_ratings()
    assert list(df["Status"]) == ["Upgrade"]
    assert list(df["Outer"]) == ["Morgan Stanley"]


def test_ticker_outer_ratings_absent_returns_none_and_warns():
    stock = _stock("quote_etf.html")
    with pytest.warns(UserWarning):
        assert stock.ticker_outer_ratings() is None


def test_ticker_news():
    df = _stock("quote_aapl.html").ticker_news()
    assert list(df["Title"]) == ["Apple beats earnings", "Analyst raises target"]
    assert list(df["Source"]) == ["Reuters", "CNBC"]


def test_ticker_inside_trader():
    df = _stock("quote_aapl.html").ticker_inside_trader()
    assert df.iloc[0]["SEC Form 4 Link"] == "https://www.sec.gov/form4/1"
    assert df.iloc[0]["Insider_id"] == "1234"
    assert df.iloc[0]["#Shares"] == 1000


def test_ticker_full_info():
    info = _stock("quote_aapl.html").ticker_full_info()
    assert set(["fundament", "ratings_outer", "news", "inside trader"]).issubset(
        info.keys()
    )


def test_ticker_signal_wall_surfaces_not_silently_dropped():
    # First call builds the quote; the screener calls that follow hit the Wall.
    use_session([html_response("quote_aapl.html"), blocked_response()])
    stock = finvizfinance("AAPL")
    with pytest.raises(FinvizBlockedError):
        stock.ticker_signal()


def test_ticker_charts_invalid_timeframe():
    stock = _stock("quote_aapl.html")
    with pytest.raises(ValueError, match=r"Invalid timeframe 'dummy'"):
        stock.ticker_charts(timeframe="dummy")


# --- Statements (routes through the resilient JSON transport) ---------------


def test_statements_real():
    use_session(FakeResponse(content=b'{"data": {"2023": {"Revenue": "100"}}}'))
    df = Statements().get_statements("AAPL")
    assert df is not None
    assert not df.empty


def test_statements_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Statements().get_statements("AAPL")


def test_statements_missing_data_raises_parse_error():
    use_session(FakeResponse(content=b"{}"))
    with pytest.raises(FinvizParseError):
        Statements().get_statements("AAPL")
