def test_group_overview():
    from finvizfinance.group.overview import Overview
    fgoverview = Overview()
    df = fgoverview.ScreenerView(group='Industry')
    assert (df is not None)