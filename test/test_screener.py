import pytest
from finvizfinance.screener.overview import Overview
from os import environ

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
    foverview = Overview()
    signals = foverview.get_signal()
    assert type(signals) is list

    filters = foverview.get_filters()
    assert type(filters) is list

    filter_options = foverview.get_filter_options('Exchange')
    assert type(filter_options) is list

    with pytest.raises(ValueError):
        foverview.get_filter_options('Dummy')


def test_screener_check_elite_with_no_auth():
    foverview = Overview()
    assert(foverview.is_elite == False)

def test_screener_check_elite_with_wrong_auth():
    foverview = Overview(use_elite=True, username='some', password='some')
    assert(foverview.is_elite == False)

def test_screener_check_elite_with_right_auth():
    foverview = Overview(use_elite=True, username='some', password='some')
    assert(foverview.is_elite == False)

def test_screener_check_elite_with_right_auth():
    if (environ.get('fv_user') and environ.get('fv_password')):
        foverview = Overview(use_elite=True, username=environ.get('fv_user'), password=environ.get('fv_password'))
        assert(foverview.is_elite == True)
    else:
        pytest.skip("Finviz Elite test requires 'fv_user' and 'fv_password' env variables properly set")

    