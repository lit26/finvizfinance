from finvizfinance.crypto import Crypto

def test_finvizfinance_crypto():
    fcrypto = Crypto()
    df = fcrypto.performance()
    assert (df is not None)


def test_finvizfinance_crypto_mock(mocker):
    mocker.patch('finvizfinance.crypto.imageScrapFunction', return_value="imagescrapfunctionurl")
    fcrypto = Crypto()
    url = fcrypto.chart(crypto='test')

    assert url == "imagescrapfunctionurl"
