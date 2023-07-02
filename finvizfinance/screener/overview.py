"""
.. module:: screen.overview
   :synopsis: screen overview table.

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
    NUMBER_COL,
    util_dict,
)


class Overview:
    """Overview
    Getting information from the finviz screener overview page.
    """

    v_page = 111

    def __init__(self):
        """initiate module"""
        self.BASE_URL = (
            "https://finviz.com/screener.ashx?v={v_page}{signal}{filter}&ft=4{ticker}"
        )
        self.url = self.BASE_URL.format(
            v_page=self.v_page, signal="", filter="", ticker=""
        )
        self._load_setting()
        self.page_count = None

    def _load_setting(self):
        """load all the signals and filters."""
        data = util_dict
        self.signal_dict = data["signal"]
        self.filter_dict = data["filter"]
        self.order_dict = data["order"]

    def _set_signal(self, signal):
        """set signal.

        Args:
            signal(str): ticker signal
        Returns:
            url_signal(str): signal string for url
        """
        url_signal = ""
        if signal not in self.signal_dict and signal != "":
            signal_keys = list(self.signal_dict.keys())
            raise ValueError(
                "Invalid signal '{}'. Possible signal: {}".format(signal, signal_keys)
            )
        elif signal != "":
            url_signal = "&s=" + self.signal_dict[signal]
        return url_signal

    def get_signal(self):
        """Get signals.

        Returns:
            signals(list): all the available trading signals
        """
        return list(self.signal_dict.keys())

    def get_filters(self):
        """Get filters.

        Returns:
            filters(list): all the available filters
        """
        return list(self.filter_dict.keys())

    def get_filter_options(self, screen_filter):
        """Get filters options.

        Args:
            screen_filter(str): screen filter for checking options

        Returns:
            filter_options(list): all the available filters
        """
        if screen_filter not in self.filter_dict:
            filter_keys = list(self.filter_dict.keys())
            raise ValueError(
                "Invalid filter '{}'. Possible filter: {}".format(
                    screen_filter, filter_keys
                )
            )
        return list(self.filter_dict[screen_filter]["option"])

    def get_orders(self):
        """Get orders.

        Returns:
            orders(list): all the available orders
        """
        return list(self.order_dict.keys())

    def _set_filters(self, filters_dict):
        """Set filters.

        Args:
            filters_dict(dict): dictionary of filters

        Returns:
            url_filter(str): filter string for url
        """
        filters = []
        for key, value in filters_dict.items():
            if key not in self.filter_dict:
                filter_keys = list(self.filter_dict.keys())
                raise ValueError(
                    "Invalid filter '{}'. Possible filter: {}".format(key, filter_keys)
                )
            if value not in self.filter_dict[key]["option"]:
                filter_options = list(self.filter_dict[key]["option"].keys())
                raise ValueError(
                    "Invalid filter option '{}'. Possible filter options: {}".format(
                        value, filter_options
                    )
                )
            prefix = self.filter_dict[key]["prefix"]
            urlcode = self.filter_dict[key]["option"][value]
            if urlcode != "":
                filters.append("{}_{}".format(prefix, urlcode))
        url_filter = ""
        if len(filters) != 0:
            url_filter = "&f=" + ",".join(filters)
        return url_filter

    def _set_ticker(self, ticker):
        """Set ticker.

        Args:
            ticker(str): ticker string
        Returns:
            url_ticker(str): ticker string for url
        """
        if ticker == "":
            return ""
        return "&t=" + ticker

    def set_filter(self, signal="", filters_dict={}, ticker=""):
        """Update the settings.

        Args:
            signal(str): ticker signal
            filters_dict(dict): dictionary of filters
            ticker(str): ticker string
        """
        if signal == "" and filters_dict == {} and ticker == "":
            self.url = self.BASE_URL.format(
                v_page=self.v_page, signal="", filter="", ticker=""
            )
        else:
            url_signal = self._set_signal(signal)
            url_filter = self._set_filters(filters_dict)
            url_ticker = self._set_ticker(ticker)
            self.url = self.BASE_URL.format(
                v_page=self.v_page,
                signal=url_signal,
                filter=url_filter,
                ticker=url_ticker,
            )

    def _get_page(self, soup):
        """Check the page number"""
        try:
            options = soup.find(id="pageSelect").findAll("option")
            self.page_count = len(options)
            return self.page_count
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
        return pd.concat([df, pd.DataFrame(frame)], ignore_index=True)

    def _screener_helper(self, i, page, rows, df, num_col_index, table_header, limit):
        """Get screener table helper function.

        Returns:
            df(pandas.DataFrame): screener information table
        """
        if i == page - 1:
            df = self._get_table(
                rows, df, num_col_index, table_header, limit=((limit - 1) % 20 + 1)
            )
        else:
            df = self._get_table(rows, df, num_col_index, table_header)
        return df

    def screener_view(
        self,
        order="ticker",
        limit=-1,
        select_page=None,
        verbose=1,
        ascend=True,
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
        url = self.url
        if order != "ticker":
            if order not in self.order_dict:
                order_keys = list(self.order_dict.keys())
                raise ValueError(
                    "Invalid order '{}'. Possible order: {}".format(order, order_keys)
                )
            url = self.url + "&" + self.order_dict[order]
        if not ascend:
            url = url.replace("o=", "o=-")
        soup = web_scrap(url)

        page = self._get_page(soup)
        if page == 0:
            print("No ticker found.")
            return None

        start_page = 1
        end_page = page

        if select_page:
            if select_page > page:
                raise ValueError("Invalid page {}".format(select_page))
            if limit != -1:
                limit = -1
                warnings.warn("Limit parameter is ignored when page is selected.")
            start_page = select_page - 1
            end_page = select_page

        if limit != -1:
            if page > (limit - 1) // 20 + 1:
                page = (limit - 1) // 20 + 1

        if verbose == 1:
            if not select_page:
                progress_bar(start_page, end_page)
            else:
                progress_bar(1, 1)

        table = soup.find("table", class_="table-light")
        rows = table.findAll("tr")
        table_header = [i.text.strip() for i in rows[0].findAll("td")][1:]
        num_col_index = [table_header.index(i) for i in table_header if i in NUMBER_COL]
        df = pd.DataFrame([], columns=table_header)
        if not select_page or select_page == 1:
            df = self._screener_helper(
                0, page, rows, df, num_col_index, table_header, limit
            )

        if select_page != 1:
            for i in range(start_page, end_page):
                sleep(sleep_sec)  # Adding sleep
                if verbose == 1:
                    if not select_page:
                        progress_bar(i + 1, page)
                    else:
                        progress_bar(1, 1)

                url = self.url
                if order == "ticker":
                    url += "&r={}".format(i * 20 + 1)
                else:
                    url += "&r={}".format(i * 20 + 1) + "&" + self.order_dict[order]
                if not ascend:
                    url = url.replace("o=", "o=-")
                soup = web_scrap(url)
                table = soup.find("table", class_="table-light")
                rows = table.findAll("tr")
                df = self._screener_helper(
                    i, page, rows, df, num_col_index, table_header, limit
                )
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
