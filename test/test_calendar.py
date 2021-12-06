def test_finvizfinance_calendar():
    from finvizfinance.calendar import Calendar
    fcalendar = Calendar()
    df = fcalendar.calendar()
    assert (df is not None)