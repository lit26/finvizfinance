import pytest
from finvizfinance.screener.overview import Overview

def test_screener_overview():
    foverview = Overview()
    filters_dict = {'Exchange': 'AMEX', 'Sector': 'Basic Materials'}
    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.screener_view()
    assert(df is not None)
    ticker = 'TSLA'
    foverview.set_filter(signal='', filters_dict={}, ticker=ticker)
    df = foverview.screener_view()
    assert(df is not None)


def test_screener_get_settings():
    foverview = Overview()
    signals = foverview.get_signal()
    assert type(signals) is list

    filters = foverview.get_filters()
    assert type(filters) is list

    filter_options = foverview.get_filter_options('Exchange')
    assert type(filter_options) is list

    with pytest.raises(ValueError):
        foverview.get_filter_options('Dummy')

