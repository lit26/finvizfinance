"""Offline fixture tests for the forex scraper (see test_quote for the pattern)."""

import pytest
from conftest import blocked_response, html_response, use_session

from finvizfinance.exceptions import FinvizBlockedError, FinvizParseError
from finvizfinance.forex import Forex


def test_forex_performance_real():
    use_session(html_response("groups_table.html"))
    df = Forex().performance()
    assert list(df["Name"]) == ["Bitcoin", "Ethereum"]


def test_forex_performance_pips():
    fake = use_session(html_response("groups_table.html"))
    Forex().performance(change="PIPS")
    assert "v=1" in fake.calls[0]["url"]


def test_forex_performance_drift_raises_parse_error():
    use_session(html_response("groups_table_drift.html"))
    with pytest.raises(FinvizParseError):
        Forex().performance()


def test_forex_performance_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Forex().performance()


def test_forex_performance_invalid_change():
    with pytest.raises(ValueError):
        Forex().performance(change="Dummy")


def test_forex_chart_url_mock(mocker):
    mocker.patch(
        "finvizfinance.forex.image_scrap_function",
        return_value="image_scrap_functionurl",
    )
    assert Forex().chart(forex="test") == "image_scrap_functionurl"


def test_forex_perf_init_json_percent_and_pips():
    # Redesigned page (#185): rows ship as JSON in script#forex-perf-init-data.
    use_session(html_response("forex_perf_init.html"))
    df = Forex().performance()
    assert df["Pair"][0] == "AUD/USD"
    assert df["Perf Day"][0] == pytest.approx(-0.0076)
    use_session(html_response("forex_perf_init.html"))
    assert Forex().performance(change="PIPS")["Perf Day"][0] == -53
