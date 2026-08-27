"""
.. module:: screener.base
   :synopsis: screen base module.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>

"""

from __future__ import annotations

import logging
import warnings
from time import sleep
from typing import Any

import pandas as pd

from finvizfinance.constants import NUMBER_COL, filter_dict, order_dict, signal_dict
from finvizfinance.quote import finvizfinance
from finvizfinance.util import (
    number_convert,
    progress_bar,
    require,
    validate_choice,
    web_scrap,
)

logger = logging.getLogger(__name__)


class Base:
    """Base
    Getting information from the finviz screener page.
    """

    v_page: int | None = None
    url = "https://finviz.com/screener.ashx"
    size = 20
    request_params: dict = {}

    def __init__(self) -> None:
        """initiate module"""
        self.reset()

    def _set_signal(self, signal: str) -> None:
        """set signal.

        Args:
            signal(str): ticker signal
        """
        if not signal:
            return
        validate_choice(signal, signal_dict, "signal")
        self.request_params["s"] = signal_dict[signal]

    def _set_filters(self, filters_dict: dict[str, str]) -> None:
        """Set filters.

        Args:
            filters_dict(dict): dictionary of filters

        Returns:
            url_filter(str): filter string for url
        """
        filters = []
        for key, value in filters_dict.items():
            validate_choice(key, filter_dict, "filter")
            validate_choice(value, filter_dict[key]["option"], "filter option")
            prefix = filter_dict[key]["prefix"]
            urlcode = filter_dict[key]["option"][value]
            if urlcode != "":
                filters.append(f"{prefix}_{urlcode}")
        if len(filters) != 0:
            self.request_params["f"] = ",".join(filters)

    def _set_ticker(self, ticker: str) -> None:
        """Set ticker.

        Args:
            ticker(str): ticker string
        """
        if ticker == "":
            return
        self.request_params["t"] = ticker

    def set_filter(
        self,
        signal: str = "",
        filters_dict: dict[str, str] | None = None,
        ticker: str = "",
    ) -> None:
        """Update the settings.

        Args:
            signal(str): ticker signal
            filters_dict(dict): dictionary of filters
            ticker(str): ticker string
        """
        if filters_dict is None:
            filters_dict = {}
        self._set_signal(signal)
        self._set_ticker(ticker)
        self._set_filters(filters_dict)

    def _get_page(self, soup: Any) -> int:
        """Check the page number"""
        select = soup.find(id="pageSelect")
        if select is None:
            return 0
        return len(select.find_all("option"))

    def _get_table(
        self,
        rows: Any,
        df: pd.DataFrame,
        num_col_index: list[int],
        table_header: list[str],
        limit: int = -1,
    ) -> pd.DataFrame:
        """Get screener table helper function.

        Returns:
            df(pandas.DataFrame): screener information table
        """
        rows = rows[1:]
        if limit != -1:
            rows = rows[0:limit]

        frame = []
        for row in rows:
            cols = row.find_all("td")[1:]
            # Build each row positionally, not keyed by header name: finviz can
            # return duplicate header labels (e.g. two "Dividend" columns in a
            # wide custom view). A name-keyed dict silently collapses those,
            # shrinking the frame's width and raising IndexError on the next
            # page once the cell count exceeds the (now shorter) header list.
            row_values = []
            for i, col in enumerate(cols):
                if i >= len(table_header):
                    break
                if table_header[i] == "Ticker" and col.has_attr("data-boxover-ticker"):
                    # The ticker cell nests two anchors (logo/company-ticker +
                    # a tab-link), so col.text repeats the symbol ("AAPL" ->
                    # "AAPLAAPL"). The clean value lives in this attribute.
                    row_values.append(col["data-boxover-ticker"])
                elif i in num_col_index:
                    row_values.append(number_convert(col.text))
                else:
                    row_values.append(col.text)
            # Pad short rows so every row matches the header width.
            row_values.extend([None] * (len(table_header) - len(row_values)))
            frame.append(row_values)
        new_df = pd.DataFrame(frame, columns=table_header)
        if len(df) == 0:
            return new_df
        return pd.concat([df, new_df], ignore_index=True)

    def _screener_table(self, soup: Any) -> Any:
        """Locate the screener results table, or raise on a Structural break."""
        return require(
            soup.find("table", class_="screener_table"),
            self.url,
            "table.screener_table",
        )

    def _parse_table_header(self, soup: Any) -> list[str]:
        table = self._screener_table(soup)
        rows = table.findAll("tr")
        table_headers = [i.text.strip() for i in rows[0].findAll("th")][1:]
        return table_headers

    def _parse_table(
        self, df: pd.DataFrame | None, soup: Any, limit: int
    ) -> pd.DataFrame:
        if df is None:
            table_headers = self._parse_table_header(soup)
            df = pd.DataFrame([], columns=table_headers)
        table_headers = list(df.columns)
        num_col_index = [
            table_headers.index(i) for i in table_headers if i in NUMBER_COL
        ]
        table = self._screener_table(soup)
        rows = table.find_all("tr")
        df = self._get_table(rows, df, num_col_index, table_headers, limit)
        return df

    def _parse_columns(self, columns: list | None) -> None:
        return

    def reset(self) -> None:
        self.request_params = {"v": self.v_page}

    def screener_view(
        self,
        order: str = "Ticker",
        limit: int = 100000,
        select_page: int | None = None,
        verbose: int = 1,
        ascend: bool = True,
        columns: list | None = None,
        sleep_sec: int = 1,
    ) -> pd.DataFrame:
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
        validate_choice(order, order_dict, "order")
        self.request_params["o"] = ("" if ascend else "-") + order_dict[order]

        if select_page:
            self.request_params["r"] = (select_page - 1) * self.size + 1

        self._parse_columns(columns)

        soup = web_scrap(self.url, self.request_params)

        page = self._get_page(soup)
        if page == 0:
            logger.warning("No ticker found.")
            return None
        df = self._parse_table(None, soup, limit)
        limit -= self.size
        if select_page:
            if select_page > page:
                return None
            warnings.warn(
                "Limit parameter is ignored when page is selected.", stacklevel=2
            )
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

    def compare(
        self,
        ticker: str,
        compare_list: list[str],
        order: str = "ticker",
        verbose: int = 1,
    ) -> pd.DataFrame:
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
            raise ValueError(f"Please check: {error_list}")

        stock = finvizfinance(ticker)
        stock_fundament = stock.ticker_fundament()
        filters_dict = {}
        for compare in compare_list:
            filters_dict[compare] = stock_fundament[compare]

        self.set_filter(filters_dict=filters_dict)
        df = self.screener_view(order=order, verbose=verbose)
        return df
