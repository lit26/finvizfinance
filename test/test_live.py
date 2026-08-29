"""Opt-in live tests that hit the real finviz site.

Unlike the rest of the suite (which injects saved HTML through the ``util``
session seam), these perform real network requests. They are **skipped by
default** so CI and a plain ``pytest test`` stay offline and deterministic.
Run them explicitly with::

    pytest --run-live
    # or target just this module:
    RUN_LIVE=1 pytest test/test_live.py

Semantics mirror ``scripts/live_smoke.py``:

* A Cloudflare **Wall** (``FinvizBlockedError`` / 403) is expected from many
  IPs (datacenter/CI especially) and tells us nothing about finviz's markup,
  so it **skips** the test rather than failing it.
* A **Drift** (``FinvizParseError``) or any other unexpected error **fails** —
  that is the actionable signal that finviz changed its markup.

Assertions check structural invariants (types, expected columns/keys, and
non-emptiness where finviz always has data) rather than exact values, which
change constantly.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

import pandas as pd
import pytest

from finvizfinance.calendar import Calendar
from finvizfinance.crypto import Crypto
from finvizfinance.earnings import Earnings
from finvizfinance.exceptions import FinvizBlockedError
from finvizfinance.forex import Forex
from finvizfinance.future import Future
from finvizfinance.group.overview import Overview as GroupOverview
from finvizfinance.insider import Insider
from finvizfinance.news import News
from finvizfinance.quote import Statements, finvizfinance
from finvizfinance.screener.overview import Overview as ScreenerOverview

# Every test in this module is a real-network test.
pytestmark = pytest.mark.live

T = TypeVar("T")


def _live(call: Callable[[], T]) -> T:
    """Run a live scrape; a Cloudflare Wall skips (expected, not Drift)."""
    try:
        return call()
    except FinvizBlockedError as exc:
        pytest.skip(f"finviz Wall (Cloudflare challenge / rate-limit): {exc}")


def _assert_columns(df: pd.DataFrame, expected: set[str]) -> None:
    """A non-empty frame must carry the expected columns (catches silent Drift).

    Emptiness is tolerated for endpoints that are legitimately empty at times
    (e.g. the economic calendar on a quiet day); a renamed/missing column while
    data *is* present is the signal we want to fail on.
    """
    if not df.empty:
        missing = expected - set(df.columns)
        assert not missing, f"missing columns {missing}; got {list(df.columns)}"


# --- quote --------------------------------------------------------------------


def test_live_quote_fundament():
    fundament = _live(lambda: finvizfinance("AAPL").ticker_fundament())
    assert isinstance(fundament, dict) and fundament
    # "Company" is required by the parser and is the most stable field.
    assert fundament.get("Company")


def test_live_quote_description():
    desc = _live(lambda: finvizfinance("AAPL").ticker_description())
    assert isinstance(desc, str) and desc.strip()


def test_live_quote_news():
    df = _live(lambda: finvizfinance("AAPL").ticker_news())
    # AAPL always has recent news; a None here means the table drifted away.
    assert isinstance(df, pd.DataFrame)
    _assert_columns(df, {"Date", "Title", "Link", "Source"})


def test_live_statements():
    # Routes through the resilient JSON transport rather than HTML scraping.
    df = _live(lambda: Statements().get_statements("AAPL"))
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- standalone pages ---------------------------------------------------------


def test_live_calendar():
    df = _live(lambda: Calendar().calendar())
    assert isinstance(df, pd.DataFrame)
    # The economic calendar can be legitimately empty (weekends/holidays).
    _assert_columns(df, {"Datetime", "Release", "Impact"})


def test_live_insider():
    df = _live(lambda: Insider().get_insider())
    assert isinstance(df, pd.DataFrame)
    _assert_columns(df, {"Ticker", "Owner", "Transaction", "SEC Form 4 Link"})


def test_live_news():
    all_news = _live(lambda: News().get_news())
    assert set(all_news) >= {"news", "blogs"}
    news = all_news["news"]
    assert isinstance(news, pd.DataFrame) and not news.empty
    _assert_columns(news, {"Date", "Title", "Source", "Link"})


# --- screener / group ---------------------------------------------------------


def test_live_screener_overview():
    # An unfiltered overview always returns rows; cap it to one small page.
    df = _live(lambda: ScreenerOverview().screener_view(limit=25, verbose=0))
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert {"Ticker", "Company"}.issubset(df.columns)


def test_live_group_overview():
    df = _live(lambda: GroupOverview().screener_view(group="Sector"))
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "Name" in df.columns


# --- performance tables (crypto / forex / futures) ----------------------------


def test_live_crypto_performance():
    df = _live(lambda: Crypto().performance())
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "Name" in df.columns


def test_live_forex_performance():
    df = _live(lambda: Forex().performance())
    assert isinstance(df, pd.DataFrame) and not df.empty
    # The forex table is keyed by currency pair (e.g. "EUR/USD"), unlike the
    # crypto/group tables which use "Name".
    assert "Pair" in df.columns


def test_live_future_performance():
    df = _live(lambda: Future().performance())
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "ticker" in df.columns


# --- earnings (composes the screeners) ----------------------------------------


def test_live_earnings_financial():
    # Earnings("This Week") raises FinvizParseError on an empty screener by
    # design, so a Drift surfaces as a failure here.
    days = _live(lambda: Earnings("This Week").partition_days("financial"))
    assert isinstance(days, dict) and days
    for frame in days.values():
        assert isinstance(frame, pd.DataFrame)
