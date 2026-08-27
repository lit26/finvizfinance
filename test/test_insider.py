"""Offline fixture tests for the insider scraper (see test_quote for the pattern)."""

import pytest

from finvizfinance.insider import Insider, INSIDER_URL
from finvizfinance.exceptions import FinvizParseError, FinvizBlockedError

from conftest import use_session, html_response, blocked_response, FakeResponse


def test_insider_real():
    use_session(html_response("insider.html"))
    df = Insider().get_insider()
    assert not df.empty
    assert df.iloc[0]["Ticker"] == "AAPL"
    assert df.iloc[0]["SEC Form 4 Link"] == "https://sec.gov/f/1"
    assert df.iloc[0]["#Shares"] == 1000


def test_insider_drift_raises_parse_error_not_indexerror():
    use_session(html_response("insider_drift.html"))
    with pytest.raises(FinvizParseError):
        Insider().get_insider()


def test_insider_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Insider()


def test_insider_missing_sec_link_is_none():
    use_session(html_response("insider_missing.html"))
    df = Insider().get_insider()
    assert df.iloc[0]["SEC Form 4 Link"] is None


def test_insider_option_urls():
    cases = {
        "latest": INSIDER_URL,
        "latest buys": INSIDER_URL + "?tc=1",
        "latest sales": INSIDER_URL + "?tc=2",
        "top week": INSIDER_URL + "?or=-10&tv=100000&tc=7&o=-transactionValue",
        "top owner sales": INSIDER_URL + "?or=10&tv=1000000&tc=2&o=-transactionValue",
        "1234": INSIDER_URL + "?oc=1234&tc=7",
    }
    for option, url in cases.items():
        fake = use_session(FakeResponse(text="<html></html>"))
        Insider(option)
        assert fake.calls[0]["url"] == url


def test_insider_invalid_option():
    use_session(FakeResponse(text="<html></html>"))
    with pytest.raises(ValueError):
        Insider("not a real option")
