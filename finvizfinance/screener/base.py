"""
.. module:: screener.base
   :synopsis: screen base module.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>

"""

from __future__ import annotations

import logging
import math
import warnings
from datetime import datetime
from time import sleep
from typing import Any

import pandas as pd

from finvizfinance.constants import (
    ETF_SCREENER_COLUMNS,
    SCREENER_COLUMNS,
    filter_dict,
    order_dict,
    signal_dict,
)
from finvizfinance.exceptions import FinvizParseError
from finvizfinance.quote import finvizfinance
from finvizfinance.util import (
    decode_json_after,
    progress_bar,
    validate_choice,
    web_scrap,
)

logger = logging.getLogger(__name__)

_COLUMNS_BY_ID = {
    **{cid: (name, kind) for cid, name, kind in SCREENER_COLUMNS.values()},
    **ETF_SCREENER_COLUMNS,
}


def _cell_value(value: Any, kind: str) -> Any:
    """Convert a raw screener JSON value to the legacy table representation."""
    if value is None or kind in ("text", "raw"):
        return value
    if kind in ("earnings", "date"):
        try:
            parsed = datetime.fromisoformat(str(value))
        except ValueError:
            return value
        if kind == "date":
            return parsed.strftime("%m/%d/%Y")
        # Legacy earnings cells read "Oct 19/b" (before open) or "/a" (after close).
        label = parsed.strftime("%b %d")
        if parsed.hour or parsed.minute:
            label += "/b" if parsed.hour < 12 else "/a"
        return label
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    if kind == "millions":
        return number * 1e6
    if kind == "pct":
        return number / 100
    return number


class Base:
    """Base
    Getting information from the finviz screener page.
    """

    v_page: int | None = None
    # False for stock-only views: the ETF screener has no such view and
    # finviz silently serves its ETF overview columns instead.
    etf_view = True
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

    def _screener_payload(self, soup: Any) -> dict:
        """Return the screener's server-side-render JSON island.

        The redesigned screener renders rows into a virtualized CSS grid (wide
        custom views only put the visible columns in the DOM), so the complete
        rows are read from this JSON island instead.
        """
        selector = "script[data-ssr-props] screener data"
        for script in soup.find_all("script", type="application/json"):
            if not script.has_attr("data-ssr-props"):
                continue
            payload = decode_json_after(script.string or "", 0, self.url, selector)
            if not isinstance(payload, dict):
                continue
            data = payload.get("data")
            if isinstance(data, dict) and isinstance(data.get("rows"), list):
                return payload
        raise FinvizParseError(url=self.url, selector=selector)

    def _screener_data(self, soup: Any) -> dict:
        """Return the screener's embedded ``data`` payload."""
        data: dict = self._screener_payload(soup)["data"]
        return data

    def _warn_etf_fallback(self, soup: Any) -> None:
        """Warn when a stock-only view was answered by the ETF screener."""
        if self.etf_view or self._screener_payload(soup).get("screenerType") != "etf":
            return
        warnings.warn(
            f"The finviz ETF screener has no {type(self).__name__} view; it "
            "returned its ETF overview columns instead. Use Overview, "
            "Performance, Technical or Custom for ETFs.",
            stacklevel=3,
        )

    def _get_page(self, soup: Any) -> int:
        """Check the page number"""
        data = self._screener_data(soup)
        total = int(data.get("totalCount") or 0)
        page_size = int(data.get("pageSize") or self.size)
        return math.ceil(total / page_size)

    def _column_ids(self, soup: Any) -> list[str]:
        """Finviz column ids of the current view, in display order."""
        if self.request_params.get("c"):
            indexes = [int(i) for i in str(self.request_params["c"]).split(",")]
            ids = [SCREENER_COLUMNS[i][0] for i in indexes if i in SCREENER_COLUMNS]
        else:
            # Preset views are narrow enough that every header is rendered.
            ids = [
                cell["data-column-id"]
                for cell in soup.select(".fv-table_header-cell[data-column-id]")
            ]
        if not ids:
            raise FinvizParseError(url=self.url, selector=".fv-table_header-cell")
        # The rank column was never part of the returned table.
        return [i for i in ids if i != "row"]

    def _parse_table(
        self, df: pd.DataFrame | None, soup: Any, limit: int
    ) -> pd.DataFrame:
        rows = self._screener_data(soup)["rows"]
        if limit != -1:
            rows = rows[0:limit]
        columns = [
            (i, *_COLUMNS_BY_ID.get(i, (i, "raw"))) for i in self._column_ids(soup)
        ]
        table_header = [name for _, name, _ in columns]
        # Build each row positionally, not keyed by header name: a view can
        # carry duplicate header labels (e.g. the two "Dividend" columns of a
        # wide custom view), which a name-keyed dict would silently collapse.
        frame = []
        for row in rows:
            text = row.get("text") or {}
            numbers = row.get("numbers") or {}
            frame.append(
                [
                    _cell_value(numbers.get(cid, text.get(cid)), kind)
                    for cid, _, kind in columns
                ]
            )
        new_df = pd.DataFrame(frame, columns=table_header)
        if df is None or len(df) == 0:
            return new_df
        return pd.concat([df, new_df], ignore_index=True)

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
        self._warn_etf_fallback(soup)
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
