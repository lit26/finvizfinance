"""Offline fixture tests for the calendar scraper (see test_quote for the pattern)."""

import pytest
from conftest import blocked_response, html_response, use_session

from finvizfinance.calendar import Calendar
from finvizfinance.exceptions import FinvizBlockedError, FinvizParseError

# --- current shape: <script id="route-init-data" type="application/json"> ------


def test_calendar_route_init_data():
    use_session(html_response("calendar_route_init.html"))
    df = Calendar().calendar()
    assert df.to_dict("records") == [
        {
            "Datetime": "Wed Aug 26, 08:30 AM",
            "Release": "Core PCE Price Index MoM",
            "Impact": "3",
            "For": "Jul",
            "Actual": "0.2%",
            "Expected": "0.2%",
            "Prior": "0.1%",
        },
        {
            "Datetime": "Mon Aug 24, 08:30 AM",
            "Release": "Chicago Fed National Activity Index",
            "Impact": "2",
            "For": "Jul",
            "Actual": "-0.08",
            "Expected": None,
            "Prior": "0.06",
        },
        {
            "Datetime": "Mon Aug 24, 11:30 AM",
            "Release": "3-Month Bill Auction",
            "Impact": "1",
            "For": None,
            "Actual": "3.715%",
            "Expected": None,
            "Prior": "3.715%",
        },
    ]


def test_calendar_route_init_empty_returns_empty_frame():
    # A quiet calendar day (entries: []) is a legitimate empty result, not Drift.
    use_session(html_response("calendar_route_init_empty.html"))
    df = Calendar().calendar()
    assert df.empty


def test_calendar_route_init_unknown_keys_raise_parse_error():
    # finviz keeps the route-init-data entries but renames every field -> the
    # normalized rows are all-None. That is Drift, not data; it must raise
    # instead of returning a table of Nones the live smoke check waves through.
    use_session(html_response("calendar_route_init_unknown_keys.html"))
    with pytest.raises(FinvizParseError) as exc:
        Calendar().calendar()
    assert exc.value.selector == "route-init-data entry fields"


def test_calendar_route_init_no_entries_raise_parse_error():
    # The route-init-data script is present but the payload no longer exposes
    # data.entries (shape moved) -> Drift.
    use_session(html_response("calendar_route_init_no_entries.html"))
    with pytest.raises(FinvizParseError) as exc:
        Calendar().calendar()
    assert exc.value.selector == "route-init-data data.entries"


# --- legacy shapes: table.calendar and FinvizInitCalendar([...]) ---------------


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
    assert df.to_dict("records") == [
        {
            "Datetime": "Mon Aug 26, 08:30 AM",
            "Release": "GDP Growth Rate",
            "Impact": "3",
            "For": "Q2",
            "Actual": "3.0%",
            "Expected": "2.8%",
            "Prior": "2.5%",
        }
    ]


def test_calendar_current_unknown_keys_raise_parse_error():
    # finviz keeps the FinvizInitCalendar call but renames every field -> the
    # normalized rows are all-None. That is Drift, not data; it must raise
    # instead of returning a table of Nones the live smoke check waves through.
    use_session(html_response("calendar_current_unknown_keys.html"))
    with pytest.raises(FinvizParseError) as exc:
        Calendar().calendar()
    assert exc.value.selector == "FinvizInitCalendar fields"


def test_calendar_current_empty_list_returns_empty_frame():
    # An empty calendar day is a legitimate empty result, not Drift.
    use_session(html_response("calendar_current_empty.html"))
    df = Calendar().calendar()
    assert df.empty


def test_calendar_drift_raises_parse_error_not_silent_empty():
    use_session(html_response("calendar_drift.html"))
    with pytest.raises(FinvizParseError) as exc:
        Calendar().calendar()
    assert (
        exc.value.selector
        == "script#route-init-data, table.calendar, or FinvizInitCalendar"
    )


def test_calendar_wall_raises_blocked_error():
    use_session(blocked_response())
    with pytest.raises(FinvizBlockedError):
        Calendar().calendar()


def test_calendar_missing_impact_is_none():
    use_session(html_response("calendar_missing.html"))
    with pytest.warns(UserWarning):
        df = Calendar().calendar()
    assert df.iloc[0]["Impact"] is None
