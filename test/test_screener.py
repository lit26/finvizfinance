def test_screener_overview():
    from finvizfinance.screener.overview import Overview
    foverview = Overview()
    filters_dict = {'Exchange': 'AMEX', 'Sector': 'Basic Materials'}
    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.ScreenerView()
    assert(df is not None)
    ticker = 'TSLA'
    foverview.set_filter(signal='', filters_dict={}, ticker=ticker)
    df = foverview.ScreenerView()
    assert(df is not None)