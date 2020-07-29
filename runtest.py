from finvizfinance.quote import finvizfinance

def test_finvizfinance_quote():
    stock = finvizfinance('tsla')
    stock_info = stock.TickerFullInfo()
    assert(stock_info is not None)
    print('Pass finvizfinance quote module')

if __name__ == "__main__":
    test_finvizfinance_quote()