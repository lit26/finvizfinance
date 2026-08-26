"""Offline fixture tests for the crypto scraper (see test_quote for the pattern)."""

import pytest

from finvizfinance.crypto import Crypto
from finvizfinance.exceptions import FinvizParseError, FinvizBlockedError

from conftest import use_session, html_response, blocked_response


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
