"""Offline fixture tests for the group views (see test_quote for the pattern)."""

import pytest

from finvizfinance.group.overview import Overview
from finvizfinance.exceptions import FinvizParseError, FinvizBlockedError

from conftest import use_session, html_response, blocked_response


def test_group_overview_real():
    use_session(html_response("groups_table.html"))
    df = Overview().screener_view(group="Industry")
    assert list(df["Name"]) == ["Bitcoin", "Ethereum"]


def test_group_drift_raises_parse_error():
    use_session(html_response("groups_table_drift.html"))
    with pytest.raises(FinvizParseError):
        Overview().screener_view(group="Industry")


def test_group_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Overview().screener_view(group="Industry")


def test_group_invalid_group():
    with pytest.raises(ValueError):
        Overview().screener_view(group="Dummy")
