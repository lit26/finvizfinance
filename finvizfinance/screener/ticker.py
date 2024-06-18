"""
.. module:: screener.ticker
   :synopsis: screen ticker table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from time import sleep
from finvizfinance.util import (
    web_scrap,
    progress_bar,
)
from finvizfinance.constants import order_dict

from finvizfinance.screener.base import Base


class Ticker(Base):
    """Financial
    Getting information from the finviz screener ticker page.
    """

    v_page = 411

    def _screener_helper(self, i, page, soup, tickers, limit):
        td = soup.find("td", class_="screener-tickers")
        page_tickers = td.find_all("span")
        if i == page - 1:
            page_tickers = page_tickers[: ((limit - 1) % 1000 + 1)]
        tickers = tickers + [i.text.split("\xa0")[1] for i in page_tickers]
        return tickers

    def screener_view(
        self, order="Ticker", limit=-1, verbose=1, ascend=True, sleep_sec=1
    ):
        """Get screener stocks.

        Args:
            order(str): sort the list by the choice of order.
            limit(int): set the top k stocks of the screener.
            verbose(int): choice of visual the progress. 1 for visualize progress.
            ascend(bool): if True, the order is ascending.
            sleep_sec(int): sleep seconds for fetching each page.
        Returns:
            tickers(list): get all the tickers as list.
        """
        if order not in order_dict:
            order_keys = list(order_dict.keys())
            raise ValueError(
                "Invalid order '{}'. Possible order: {}".format(order, order_keys)
            )
        self.request_params["o"] = ("" if ascend else "-") + order_dict[order]
        soup = web_scrap(self.url, self.request_params)
        page = self._get_page(soup)
        if page == 0:
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
            sleep(sleep_sec)  # Adding sleep
            if verbose == 1:
                progress_bar(i + 1, page)
            self.request_params["r"] = i * 1000 + 1
            soup = web_scrap(self.url, self.request_params)
            tickers = self._screener_helper(i, page, soup, tickers, limit)
        return tickers
