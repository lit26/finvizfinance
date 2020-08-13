from finvizfinance.quote import finvizfinance
from finvizfinance.news import News
from finvizfinance.insider import Insider
from finvizfinance.forex import Forex
from finvizfinance.crypto import Crypto
from finvizfinance.screener.overview import Overview

def test_finvizfinance_quote():
    stock = finvizfinance('tsla')
    stock_info = stock.TickerFullInfo()
    assert(stock_info is not None)

def test_finvizfinance_news():
    fnews = News()
    all_news = fnews.getNews()
    news = all_news['news']
    blogs = all_news['blogs']
    assert(news is not None)
    assert(blogs is not None)

def test_finvizfinance_insider():
    finsider = Insider(option='top owner trade')
    insider = finsider.getInsider()
    assert(insider is not None)

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

def test_finvizfinance_forex():
    fforex = Forex()
    df = fforex.performance()
    assert (df is not None)

def test_finvizfinance_crypto():
    fcrypto = Crypto()
    df = fcrypto.performance()
    assert (df is not None)

if __name__ == "__main__":
    test_finvizfinance_quote()
    print('Quote module test pass.')
    test_finvizfinance_news()
    print('News module test pass.')
    test_finvizfinance_insider()
    print('Insider module test pass.')
    test_screener_overview()
    print('Screener module test pass.')
    test_finvizfinance_forex()
    print('Forex module test pass.')
    test_finvizfinance_crypto()
    print('Crypto module test pass.')