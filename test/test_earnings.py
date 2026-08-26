"""Offline fixture tests for the earnings exporter (composes the screeners)."""

import pytest

from finvizfinance.earnings import Earnings
from finvizfinance.exceptions import FinvizParseError, FinvizBlockedError

from conftest import use_session, html_response, blocked_response


def test_earnings_partition_financial():
    use_session(html_response("earnings_screener.html"))
    earnings = Earnings("This Week")
    days = earnings.partition_days("financial")
    assert set(days.keys()) == {"May 02", "May 03"}
    assert len(days["May 02"]) == 2
    assert len(days["May 03"]) == 1


def test_earnings_partition_overview():
    # Overview mode fetches a second screener; the fake session repeats it.
    use_session(html_response("earnings_screener.html"))
    earnings = Earnings("This Week")
    days = earnings.partition_days("overview")
    assert set(days["May 02"]["Ticker"]) == {"AAPL", "MSFT"}


def test_earnings_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Earnings("This Week")


def test_earnings_drift_raises_parse_error():
    use_session(html_response("screener_drift.html"))
    with pytest.raises(FinvizParseError):
        Earnings("This Week")


def test_earnings_no_results_raises_parse_error():
    use_session(html_response("screener_noresults.html"))
    with pytest.raises(FinvizParseError):
        Earnings("This Week")


def test_earnings_invalid_period():
    with pytest.raises(ValueError):
        Earnings("Invalid Period")
