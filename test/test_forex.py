import pytest
from finvizfinance.forex import Forex


def test_forex_performance_percentage():
    fforex = Forex()
    df = fforex.performance()
    assert (df is not None)


def test_forex_performance_pips():
    fforex = Forex()
    df = fforex.performance(change='PIPS')
    assert (df is not None)


def test_forex_performance_error():
    with pytest.raises(ValueError):
        fforex = Forex()
        fforex.performance(change='Dummy')


def test_forex_chart_none():
    fforex = Forex()
    fforex.chart()

