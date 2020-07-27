from finvizfinance.screener.overview import Overview
from finvizfinance.util import webScrap

class Ticker(Overview):
    def __init__(self):
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=411{filter}&ft=4'
        self.url = self.BASE_URL.format(filter='')
        self._loadfilter()

    def ScreenerView(self, verbose=1):
        soup = webScrap(self.url)
        page = self._get_page(soup)
        if page == 0:
            print('No ticker found.')
            return None

        if verbose == 1:
            print('[Info] loading page 1/{} ...'.format(page))
        table = soup.findAll('table')[18]
        tickers = table.findAll('span')
        tickers = [i.text.split('\xa0')[1] for i in tickers]

        for i in range(1, page):
            print('[Info] loading page {}/{} ...'.format((i + 1), page))
            soup = webScrap(self.url + '&r={}'.format(i * 1000 + 1))
            table = soup.findAll('table')[18]
            page_tickers = table.findAll('span')
            tickers = tickers + [i.text.split('\xa0')[1] for i in page_tickers]
        return tickers