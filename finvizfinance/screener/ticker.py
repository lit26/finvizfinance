"""
.. module:: screen.ticker
   :synopsis: screen ticker table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
from time import sleep
from finvizfinance.screener.overview import Overview
from finvizfinance.util import web_scrap, progress_bar


class Ticker(Overview):
    """Financial inherit from overview module.
    Getting information from the finviz screener ticker page.
    """

    v_page = 411

    def _screener_helper(self, i, page, soup, tickers, limit):
        td = soup.find("td", class_="screener-tickers")
        page_tickers = td.findAll("span")
        if i == page - 1:
            page_tickers = page_tickers[: ((limit - 1) % 1000 + 1)]
        tickers = tickers + [i.text.split("\xa0")[1] for i in page_tickers]
        return tickers

    def screener_view(
        self, order="ticker", limit=-1, verbose=1, ascend=True, sleep_sec=1
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
        url = self.url
        if order != "ticker":
            if order not in self.order_dict:
                order_keys = list(self.order_dict.keys())
                raise ValueError(f"Invalid order '{order}'. Possible order: {order_keys}")
            url = f"{self.url}&{self.order_dict[order]}"
        if not ascend:
            url = url.replace("o=", "o=-")
        soup = web_scrap(url)
        page = self._get_page(soup)
        if page == 0:
            if verbose == 1:
                print("No ticker found.")
            return None

        if limit != -1 and page > (limit - 1) // 1000 + 1:
            page = (limit - 1) // 1000 + 1

        if verbose == 1:
            progress_bar(1, page)

        tickers = []
        tickers = self._screener_helper(0, page, soup, tickers, limit)

        for i in range(1, page):
            sleep(sleep_sec)  # Adding sleep
            if verbose == 1:
                progress_bar(i + 1, page)
            soup = web_scrap(f"{self.url}&r={i * 1000 + 1}")
            tickers = self._screener_helper(i, page, soup, tickers, limit)
        return tickers
