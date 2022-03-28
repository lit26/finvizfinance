from finvizfinance.screener.overview import Overview
from finvizfinance.util import web_scrap, progress_bar

"""
.. module:: screen.ticker
   :synopsis: screen ticker table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

SCREENER_TABLE_INDEX = 21


class Ticker(Overview):
    """Financial inherit from overview module.
    Getting information from the finviz screener ticker page.

    Args:
        screener_table_index(int): table index of the stock screener. change only if change on finviz side.
    """

    def __init__(self, screener_table_index=SCREENER_TABLE_INDEX):
        """initiate module"""
        self._screener_table_index = screener_table_index
        self.BASE_URL = (
            "https://finviz.com/screener.ashx?v=411{signal}{filter}&ft=4{ticker}"
        )
        self.url = self.BASE_URL.format(signal="", filter="", ticker="")
        Overview._load_setting(self)

    def _screener_helper(self, i, page, soup, tickers, limit):
        table = soup.findAll("table")[self._screener_table_index]
        page_tickers = table.findAll("span")
        if i == page - 1:
            page_tickers = page_tickers[: ((limit - 1) % 1000 + 1)]
        tickers = tickers + [i.text.split("\xa0")[1] for i in page_tickers]
        return tickers

    def screener_view(self, limit=-1, verbose=1):
        """Get screener table.

        Args:
            verbose(int): choice of visual the progress. 1 for visualize progress.
        Returns:
            tickers(list): get all the tickers as list.
        """
        soup = web_scrap(self.url)
        page = self._get_page(soup)
        if page == 0:
            if verbose == 1:
                print("No ticker found.")
            return None

        if limit != -1:
            if page > (limit - 1) // 1000 + 1:
                page = (limit - 1) // 1000 + 1

        if verbose == 1:
            progress_bar(1, page)

        tickers = []
        tickers = self._screener_helper(0, page, soup, tickers, limit)

        for i in range(1, page):
            if verbose == 1:
                progress_bar(i + 1, page)
            soup = web_scrap(self.url + "&r={}".format(i * 1000 + 1))
            tickers = self._screener_helper(i, page, soup, tickers, limit)
        return tickers
