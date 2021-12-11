from finvizfinance.insider import Insider


def test_finvizfinance_insider():
    finsider = Insider()
    insider = finsider.get_insider()
    assert(insider is not None)


def test_finvizfinance_insider_option(mocker):
    web_scrap_mock = mocker.patch('finvizfinance.insider.web_scrap', return_value="dummy web scrap")
    Insider()
    web_scrap_mock.assert_called_with('https://finviz.com/insidertrading.ashx')
    Insider('latest buys')
    web_scrap_mock.assert_called_with('https://finviz.com/insidertrading.ashx?tc=1')
    Insider('latest sales')
    web_scrap_mock.assert_called_with('https://finviz.com/insidertrading.ashx?tc=2')
    Insider('top week')
    web_scrap_mock.assert_called_with(
        'https://finviz.com/insidertrading.ashx?or=-10&tv=100000&tc=7&o=-transactionValue')
    Insider('top week buys')
    web_scrap_mock.assert_called_with(
        'https://finviz.com/insidertrading.ashx?or=-10&tv=100000&tc=1&o=-transactionValue')
    Insider('top week sales')
    web_scrap_mock.assert_called_with(
        'https://finviz.com/insidertrading.ashx?or=-10&tv=100000&tc=2&o=-transactionValue')
    Insider('top owner trade')
    web_scrap_mock.assert_called_with(
        'https://finviz.com/insidertrading.ashx?or=10&tv=1000000&tc=7&o=-transactionValue')
    Insider('top owner buys')
    web_scrap_mock.assert_called_with(
        'https://finviz.com/insidertrading.ashx?or=10&tv=1000000&tc=1&o=-transactionValue')
    Insider('top owner sales')
    web_scrap_mock.assert_called_with(
        'https://finviz.com/insidertrading.ashx?or=10&tv=1000000&tc=2&o=-transactionValue')
    insider_id = '1234'
    Insider(insider_id)
    web_scrap_mock.assert_called_with(
        'https://finviz.com/insidertrading.ashx?oc=' + insider_id + '&tc=7')