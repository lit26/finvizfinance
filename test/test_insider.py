def test_finvizfinance_insider():
    from finvizfinance.insider import Insider
    finsider = Insider(option='top owner trade')
    insider = finsider.getInsider()
    assert(insider is not None)