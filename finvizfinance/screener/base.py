"""
.. module:: screener.base
   :synopsis: screen base module.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>

"""

import warnings
import pandas as pd
from time import sleep
from finvizfinance.quote import finvizfinance
from finvizfinance.util import (
    web_scrap,
    number_covert,
    progress_bar,
)
from finvizfinance.constants import NUMBER_COL, signal_dict, filter_dict, order_dict


class Base:
    """Base
    Getting information from the finviz screener page.
    """

    v_page = None
    url = "https://finviz.com/screener.ashx"
    size = 20
    request_params = {}

    def __init__(self):
        """initiate module"""
        self.reset()

    def _set_signal(self, signal):
        """set signal.

        Args:
            signal(str): ticker signal
        """
        if not signal:
            return
        if signal not in signal_dict:
            signal_keys = list(signal_dict.keys())
            raise ValueError(
                "Invalid signal '{}'. Possible signal: {}".format(signal, signal_keys)
            )
        self.request_params["s"] = signal_dict[signal]

    def _set_filters(self, filters_dict):
        """Set filters.

        Args:
            filters_dict(dict): dictionary of filters

        Returns:
            url_filter(str): filter string for url
        """
        filters = []
        for key, value in filters_dict.items():
            if key not in filter_dict:
                filter_keys = list(filter_dict.keys())
                raise ValueError(
                    "Invalid filter '{}'. Possible filter: {}".format(key, filter_keys)
                )
            if value not in filter_dict[key]["option"]:
                filter_options = list(filter_dict[key]["option"].keys())
                raise ValueError(
                    "Invalid filter option '{}'. Possible filter options: {}".format(
                        value, filter_options
                    )
                )
            prefix = filter_dict[key]["prefix"]
            urlcode = filter_dict[key]["option"][value]
            if urlcode != "":
                filters.append("{}_{}".format(prefix, urlcode))
        if len(filters) != 0:
            self.request_params["f"] = ",".join(filters)

    def _set_ticker(self, ticker):
        """Set ticker.

        Args:
            ticker(str): ticker string
        """
        if ticker == "":
            return
        self.request_params["t"] = ticker

    def set_filter(self, signal="", filters_dict={}, ticker=""):
        """Update the settings.

        Args:
            signal(str): ticker signal
            filters_dict(dict): dictionary of filters
            ticker(str): ticker string
        """
        self._set_signal(signal)
        self._set_ticker(ticker)
        self._set_filters(filters_dict)

    def _get_page(self, soup):
        """Check the page number"""
        try:
            options = soup.find(id="pageSelect").findAll("option")
            return len(options)
        except:
            return 0

    def _get_table(self, rows, df, num_col_index, table_header, limit=-1):
        """Get screener table helper function.

        Returns:
            df(pandas.DataFrame): screener information table
        """
        rows = rows[1:]
        if limit != -1:
            rows = rows[0:limit]

        frame = []
        for row in rows:
            cols = row.findAll("td")[1:]
            info_dict = {}
            for i, col in enumerate(cols):
                # check if the col is number
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                else:
                    info_dict[table_header[i]] = number_covert(col.text)
            frame.append(info_dict)
        if len(df) == 0:
            return pd.DataFrame(frame)
        else:
            return pd.concat([df, pd.DataFrame(frame)], ignore_index=True)

    @staticmethod
    def _parse_table_header(soup):
        table = soup.find("table", class_="screener_table")
        rows = table.findAll("tr")
        table_headers = [i.text.strip() for i in rows[0].findAll("th")][1:]
        return table_headers

    def _parse_table(self, df, soup, limit):
        if df is None:
            table_headers = self._parse_table_header(soup)
            df = pd.DataFrame([], columns=table_headers)
        table_headers = list(df.columns)
        num_col_index = [
            table_headers.index(i) for i in table_headers if i in NUMBER_COL
        ]
        table = soup.find("table", class_="screener_table")
        rows = table.find_all("tr")
        df = self._get_table(rows, df, num_col_index, table_headers, limit)
        return df

    def _parse_columns(self, columns):
        return

    def reset(self):
        self.request_params = {"v": self.v_page}

    def screener_view(
        self,
        order="Ticker",
        limit=100000,
        select_page=None,
        verbose=1,
        ascend=True,
        columns=None,
        sleep_sec=1,
    ):
        """Get screener table.

        Args:
            order(str): sort the table by the choice of order.
            limit(int): set the top k rows of the screener.
            select_page(int): set the page of the screener.
            verbose(int): choice of visual the progress. 1 for visualize progress.
            ascend(bool): if True, the order is ascending.
            sleep_sec(int): sleep seconds for fetching each page.
        Returns:
            df(pandas.DataFrame): screener information table
        """
        if order not in order_dict:
            order_keys = list(order_dict.keys())
            raise ValueError(
                "Invalid order '{}'. Possible order: {}".format(order, order_keys)
            )
        self.request_params["o"] = ("" if ascend else "-") + order_dict[order]

        if select_page:
            self.request_params["r"] = (select_page - 1) * self.size + 1

        self._parse_columns(columns)

        soup = web_scrap(self.url, self.request_params)

        page = self._get_page(soup)
        if page == 0:
            print("No ticker found.")
            return None
        df = self._parse_table(None, soup, limit)
        limit -= self.size
        if select_page:
            if select_page > page:
                return None
            warnings.warn("Limit parameter is ignored when page is selected.")
            return df

        for i in range(1, page):
            if limit <= 0:
                break
            sleep(sleep_sec)
            if verbose == 1:
                progress_bar(i, page)
            self.request_params["r"] = i * self.size + 1
            soup = web_scrap(self.url, self.request_params)
            df = self._parse_table(df, soup, limit)
            limit -= self.size
        self.reset()
        return df

    def compare(self, ticker, compare_list, order="ticker", verbose=1):
        """Get screener table of similar property (Sector, Industry, Country)

        Args:
            ticker(str): the ticker to compare
            compare_list(list): choice of compare property (Sector, Industry, Country) or combination.
            order(str): sort the table by the choice of order
            verbose(int): choice of visual the progress. 1 for visualize progress
        Returns:
            df(pandas.DataFrame): screener information table
        """
        check_list = ["Sector", "Industry", "Country"]
        error_list = [i for i in compare_list if i not in check_list]
        if len(error_list) != 0:
            raise ValueError("Please check: {}".format(error_list))

        stock = finvizfinance(ticker)
        stock_fundament = stock.ticker_fundament()
        filters_dict = {}
        for compare in compare_list:
            filters_dict[compare] = stock_fundament[compare]

        self.set_filter(filters_dict=filters_dict)
        df = self.screener_view(order=order, verbose=verbose)
        return df
