def test_group_overview():
    from finvizfinance.group.overview import Overview
    fgoverview = Overview()
    df = fgoverview.screener_view(group='Industry')
    assert (df is not None)