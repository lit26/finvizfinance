import pytest
from finvizfinance.util import web_scrap, set_proxy


def test_proxy(mocker):
    proxy_mock = mocker.patch('finvizfinance.util.session.get', return_value="data")
    with pytest.raises(AttributeError):
        web_scrap('http://test.com')
        proxy_mock.assert_called_with(proxies=None)

    proxies = {
        'http': 'http://10.10.1.10:3128',
        'https': 'http://10.10.1.10:1080',
    }
    set_proxy(proxies)
    with pytest.raises(AttributeError):
        web_scrap('http://test.com')
        proxy_mock.assert_called_with(proxies=proxies)