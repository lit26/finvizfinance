from finvizfinance.screener.overview import Overview
from finvizfinance.util import webScrap, progressBar
"""
.. module:: screen.ticker
   :synopsis: screen ticker table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


class Ticker(Overview):
    """Financial inherit from overview module.
    Getting information from the finviz screener ticker page.
    """
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=411{signal}{filter}&ft=4{ticker}'
        self.url = self.BASE_URL.format(signal='', filter='', ticker='')
        Overview._loadSetting(self)

    def _screener_helper(self, i, page, soup, tickers, limit):
        table = soup.findAll('table')[18]
        page_tickers = table.findAll('span')
        if i == page - 1:
            page_tickers = page_tickers[:((limit - 1) % 1000 + 1)]
        tickers = tickers + [i.text.split('\xa0')[1] for i in page_tickers]
        return tickers

    def ScreenerView(self, limit=-1, verbose=1):
        """Get screener table.

        Args:
            verbose(int): choice of visual the progress. 1 for visualize progress.
        Returns:
            tickers(list): get all the tickers as list.
        """
        soup = webScrap(self.url)
        page = self._get_page(soup)
        if page == 0:
            if verbose == 1:
                print('No ticker found.')
            return None

        if limit != -1:
            if page > (limit-1)//1000+1:
                page = (limit-1)//1000+1

        if verbose == 1:
            progressBar(1, page)

        tickers = []
        tickers = self._screener_helper(0, page, soup, tickers, limit)

        for i in range(1, page):
            if verbose == 1:
                progressBar(i+1, page)
            soup = webScrap(self.url + '&r={}'.format(i * 1000 + 1))
            tickers = self._screener_helper(i, page, soup, tickers, limit)
        return tickers