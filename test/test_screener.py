import pytest
from finvizfinance.screener import (
    Overview,
    get_signal,
    get_filters,
    get_filter_options
)


def test_screener_overview():
    foverview = Overview()
    filters_dict = {'Exchange': 'AMEX', 'Sector': 'Basic Materials'}
    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.screener_view(order="Company", ascend=False)
    assert(df is not None)
    ticker = 'TSLA'
    foverview.set_filter(signal='', filters_dict={}, ticker=ticker)
    df = foverview.screener_view()
    assert(df is not None)


def test_screener_get_settings():
    signals = get_signal()
    assert type(signals) is list

    filters = get_filters()
    assert type(filters) is list

    filter_options = get_filter_options('Exchange')
    assert type(filter_options) is list

    with pytest.raises(ValueError):
        get_filter_options('Dummy')
