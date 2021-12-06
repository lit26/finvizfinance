def test_finvizfinance_crypto():
    from finvizfinance.crypto import Crypto
    fcrypto = Crypto()
    df = fcrypto.performance()
    assert (df is not None)