from finvizfinance.quote import finvizfinance
from finvizfinance.news import News
from finvizfinance.insider import Insider
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

if __name__ == "__main__":
    test_finvizfinance_quote()
    test_finvizfinance_news()
    test_finvizfinance_insider()
    test_screener_overview()