def test_finvizfinance_forex():
    from finvizfinance.forex import Forex
    fforex = Forex()
    df = fforex.performance()
    assert (df is not None)