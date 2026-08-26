"""Offline fixture tests for the calendar scraper (see test_quote for the pattern)."""

import pytest

from finvizfinance.calendar import Calendar
from finvizfinance.exceptions import FinvizParseError, FinvizBlockedError

from conftest import use_session, html_response, blocked_response


def test_calendar_real():
    use_session(html_response("calendar.html"))
    df = Calendar().calendar()
    assert len(df) == 2
    assert df.iloc[0]["Release"] == "GDP Growth Rate"
    assert df.iloc[0]["Impact"] == "3"
    assert df.iloc[0]["Datetime"].startswith("Mon Aug 26")


def test_calendar_current_client_rendered_format():
    use_session(html_response("calendar_current.html"))
    df = Calendar().calendar()
    assert df.to_dict("records") == [{
        "Datetime": "Mon Aug 26, 08:30 AM", "Release": "GDP Growth Rate",
        "Impact": "3", "For": "Q2", "Actual": "3.0%",
        "Expected": "2.8%", "Prior": "2.5%",
    }]


def test_calendar_drift_raises_parse_error_not_silent_empty():
    use_session(html_response("calendar_drift.html"))
    with pytest.raises(FinvizParseError) as exc:
        Calendar().calendar()
    assert exc.value.selector == "table.calendar or FinvizInitCalendar"


def test_calendar_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Calendar().calendar()


def test_calendar_missing_impact_is_none():
    use_session(html_response("calendar_missing.html"))
    with pytest.warns(UserWarning):
        df = Calendar().calendar()
    assert df.iloc[0]["Impact"] is None
