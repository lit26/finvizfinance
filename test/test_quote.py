def test_finvizfinance_quote():
    from finvizfinance.quote import finvizfinance
    stock = finvizfinance('tsla')
    stock_info = stock.TickerFullInfo()
    assert(stock_info is not None)