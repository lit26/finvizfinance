import pytest
from finvizfinance.screener.overview import Overview

def test_screener_overview():
    foverview = Overview()
    filters_dict = {'Exchange': 'AMEX', 'Sector': 'Basic Materials'}
    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.ScreenerView()
    assert(df is not None)
    ticker = 'TSLA'
    foverview.set_filter(signal='', filters_dict={}, ticker=ticker)
    df = foverview.ScreenerView()
    assert(df is not None)


def test_screener_get_settings():
    foverview = Overview()
    signals = foverview.getSignal()
    assert type(signals) is list

    filters = foverview.getFilters()
    assert type(filters) is list

    filter_options = foverview.getFilterOptions('Exchange')
    assert type(filter_options) is list

    with pytest.raises(ValueError):
        foverview.getFilterOptions('Dummy')

