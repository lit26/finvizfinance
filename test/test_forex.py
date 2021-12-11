import pytest
from finvizfinance.forex import Forex


def test_forex_performance_percentage():
    fforex = Forex()
    df = fforex.performance()
    assert (df is not None)


def test_forex_performance_pips(mocker):
    mocker.patch('finvizfinance.forex.scrap_function', return_value="df")
    fforex = Forex()
    df = fforex.performance(change='PIPS')
    assert (df is not None)


def test_finvizfinance_crypto_mock(mocker):
    mocker.patch('finvizfinance.forex.image_scrap_function', return_value="image_scrap_functionurl")
    fforex = Forex()
    url = fforex.chart(forex='test')

    assert url == "image_scrap_functionurl"


def test_forex_performance_error():
    with pytest.raises(ValueError):
        fforex = Forex()
        fforex.performance(change='Dummy')

