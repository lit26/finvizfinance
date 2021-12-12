from finvizfinance.crypto import Crypto

def test_finvizfinance_crypto():
    fcrypto = Crypto()
    df = fcrypto.performance()
    assert (df is not None)


def test_finvizfinance_crypto_mock(mocker):
    mocker.patch('finvizfinance.crypto.image_scrap_function', return_value="image_scrap_functionurl")
    fcrypto = Crypto()
    url = fcrypto.chart(crypto='test')

    assert url == "image_scrap_functionurl"
