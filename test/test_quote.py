import pytest
from finvizfinance.quote import finvizfinance, Quote, Statements


# def test_finvizfinance_quote(mocker):
#     web_scrap_mock = mocker.patch('finvizfinance.quote.webScrap', return_value={"text": 'webScrap'})
#     Quote().getCurrent('ticker')
#     web_scrap_mock.assert_called_with('https://finviz.com/request_quote.ashx?t=ticker')


def test_finvizfinance_finvizfinance():
    stock = finvizfinance('tsla')
    stock_info = stock.TickerFullInfo()
    assert(stock_info is not None)


def test_finvizfinance_finvizfinance_chart_invalid(mocker):
    mocker.patch('finvizfinance.quote.finvizfinance._checkexist', return_value=True)
    mocker.patch('finvizfinance.quote.webScrap', return_value="")
    with pytest.raises(ValueError, match=r"Invalid timeframe 'dummy'"):
        finvizfinance('tsla').TickerCharts(timeframe='dummy')


def test_statements():
    fstatments = Statements()
    df = fstatments.getStatements('tsla')
    assert (df is not None)

    with pytest.raises(ValueError, match=r"Invalid chart type 'dummy'"):
        finvizfinance('tsla').TickerCharts(charttype='dummy')


def test_finvizfinance_finvizfinance_chart(mocker):
    mocker.patch('finvizfinance.quote.finvizfinance._checkexist', return_value=True)
    mocker.patch('finvizfinance.quote.webScrap', return_value="")
    image_scrap_mock = mocker.patch('finvizfinance.quote.imageScrap')
    finvizfinance('dummy').TickerCharts()
    image_scrap_mock.assert_called_with(
        'https://finviz.com/chart.ashx?t=dummy&ty=c&ta=1&p=d', 'dummy', '')
