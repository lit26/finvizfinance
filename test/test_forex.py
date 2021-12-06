import pytest
from finvizfinance.forex import Forex

def test_finvizfinance_forex():
    fforex = Forex()
    df = fforex.performance()
    assert (df is not None)


def test_forex_performance_pips(mocker):
    mocker.patch('finvizfinance.forex.scrapFunction', return_value="df")
    fforex = Forex()
    df = fforex.performance(change='PIPS')
    assert (df is not None)


def test_forex_performance_error():
    with pytest.raises(ValueError):
        fforex = Forex()
        fforex.performance(change='Dummy')

