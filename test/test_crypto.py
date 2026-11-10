"""Offline fixture tests for the crypto scraper (see test_quote for the pattern)."""

import pytest
from conftest import blocked_response, html_response, use_session

from finvizfinance.crypto import Crypto
from finvizfinance.exceptions import FinvizBlockedError, FinvizParseError


def test_crypto_performance_real():
    use_session(html_response("groups_table.html"))
    df = Crypto().performance()
    assert list(df["Name"]) == ["Bitcoin", "Ethereum"]
    assert df.iloc[0]["Change"] == 0.025


def test_crypto_performance_drift_raises_parse_error():
    use_session(html_response("groups_table_drift.html"))
    with pytest.raises(FinvizParseError):
        Crypto().performance()


def test_crypto_performance_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Crypto().performance()


def test_crypto_chart_url_mock(mocker):
    mocker.patch(
        "finvizfinance.crypto.image_scrap_function",
        return_value="image_scrap_functionurl",
    )
    assert Crypto().chart(crypto="test") == "image_scrap_functionurl"


def test_crypto_performance_perf_init_json():
    # Redesigned page (#185): rows ship as JSON in script#crypto-perf-init-data.
    use_session(html_response("crypto_perf_init.html"))
    df = Crypto().performance()
    assert list(df["Name"]) == ["Aave", "Cardano"]
    assert df["Ticker"][0] == "AAVEUSD"
    assert df["Perf Day"][0] == pytest.approx(-0.0109)
