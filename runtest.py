from finvizfinance.quote import finvizfinance

def test_finvizfinance():
    stock = finvizfinance('tsla')
    stock_fundament = stock.TickerFundament()
    assert(stock_fundament is not None)
    print('OK')

if __name__ == "__main__":
    test_finvizfinance()