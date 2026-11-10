"""
.. module:: screener.base
   :synopsis: screen base module.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>

"""

from __future__ import annotations

import json
import logging
import math
import warnings
from time import sleep
from typing import Any

import pandas as pd

from finvizfinance.constants import NUMBER_COL, filter_dict, order_dict, signal_dict
from finvizfinance.exceptions import FinvizParseError
from finvizfinance.quote import finvizfinance
from finvizfinance.util import (
    number_convert,
    progress_bar,
    require,
    validate_choice,
    web_scrap,
)

logger = logging.getLogger(__name__)

# The redesigned screener (Oct 2026) labels a few columns differently from the
# old table. Map them back so existing column names keep working.
LEGACY_LABELS = {
    "Change %": "Change",
    "Change from Open %": "Change from Open",
    "Forward P/E": "Fwd P/E",
}


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _colindex(cell: Any) -> int:
    try:
        return int(cell.get("aria-colindex", 0))
    except ValueError:
        return 0


class Base:
    """Base
    Getting information from the finviz screener page.
    """

    v_page: int | None = None
    url = "https://finviz.com/screener.ashx"
    size = 20
    request_params: dict = {}
    # (soup, data) of the last parsed SSR island, so one page is decoded once.
    _ssr_cache: tuple[Any, dict | None] | None = None

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

    def _ssr_data(self, soup: Any) -> dict | None:
        """Return the ``data`` payload of the screener's SSR island.

        The redesigned screener embeds its results as JSON in
        ``<script type="application/json" data-ssr-props>``. Returns ``None``
        when the island is absent (the legacy table page); an island without a
        usable ``data`` object is finviz Drift and raises.
        """
        if self._ssr_cache is not None and self._ssr_cache[0] is soup:
            return self._ssr_cache[1]
        data = self._load_ssr_data(soup)
        self._ssr_cache = (soup, data)
        return data

    def _load_ssr_data(self, soup: Any) -> dict | None:
        tag = soup.find(
            "script", attrs={"type": "application/json", "data-ssr-props": True}
        )
        if tag is None:
            return None
        selector = "script[data-ssr-props] data"
        try:
            payload = json.loads(tag.string or tag.get_text())
        except (json.JSONDecodeError, TypeError) as err:
            raise FinvizParseError(url=self.url, selector=selector) from err
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict) or not _is_int(data.get("totalCount")):
            raise FinvizParseError(url=self.url, selector=selector)
        return data

    def _get_page(self, soup: Any) -> int:
        """Check the page number"""
        data = self._ssr_data(soup)
        if data is not None:
            # Paging offsets (r=) and the limit countdown step by self.size, so
            # a different server page size would skip or repeat rows.
            page_size = data.get("pageSize", self.size)
            if page_size != self.size:
                raise FinvizParseError(
                    f"Screener page size {page_size!r} at {self.url} does not "
                    f"match the expected {self.size}. Finviz markup may have "
                    "changed (Drift).",
                    url=self.url,
                    selector="script[data-ssr-props] data.pageSize",
                )
            total: int = data["totalCount"]
            return math.ceil(total / self.size)
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

        Args:
            rows(list): one list of cells per row, the "No." cell excluded.
        Returns:
            df(pandas.DataFrame): screener information table
        """
        if limit != -1:
            rows = rows[0:limit]

        frame = []
        for cols in rows:
            # Build each row positionally, not keyed by header name: finviz can
            # return duplicate header labels (e.g. two "Dividend" columns in a
            # wide custom view). A name-keyed dict silently collapses those,
            # shrinking the frame's width and raising IndexError on the next
            # page once the cell count exceeds the (now shorter) header list.
            row_values = []
            for i, col in enumerate(cols):
                if i >= len(table_header):
                    break
                ticker = col.get("data-boxover-ticker") or col.get("data-ticker")
                if table_header[i] == "Ticker" and ticker:
                    # The ticker cell nests extra markup (a logo tile, or a
                    # second tab-link anchor), so col.text repeats the symbol
                    # ("AAPL" -> "AAPLAAPL"). The clean value lives in an
                    # attribute: data-boxover-ticker (legacy) or data-ticker.
                    row_values.append(ticker)
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

    def _screener_grid(self, soup: Any) -> Any:
        """Locate the redesigned results grid, or raise on a Structural break."""
        return require(
            soup.find(attrs={"role": "grid", "aria-label": "Screener results"}),
            self.url,
            "div[role=grid] Screener results",
        )

    @staticmethod
    def _grid_cells(row: Any, role: str) -> list[Any]:
        """Cells of a grid row in column order, without the "No." column.

        The grid splits columns across lanes (pinned left, scrolling center),
        so order by aria-colindex rather than trusting document order.
        """
        cells = [
            cell
            for cell in row.find_all(attrs={"role": role})
            if cell.get("data-column-id") != "row"
        ]
        return sorted(cells, key=_colindex)

    def _parse_table_header(self, soup: Any) -> list[str]:
        if self._ssr_data(soup) is not None:
            grid = self._screener_grid(soup)
            cells = self._grid_cells(grid, "columnheader")
            # The grid virtualizes columns that don't fit the server's assumed
            # viewport (~38 in a wide custom view): they are counted in
            # aria-colcount but never rendered. Fail loudly rather than return
            # a silently narrower table. (+1 for the excluded "No." column.)
            colcount = grid.get("aria-colcount")
            if colcount and colcount.isdigit() and len(cells) + 1 < int(colcount):
                raise FinvizParseError(
                    f"Screener grid at {self.url} rendered {len(cells) + 1} of "
                    f"{colcount} columns. Request fewer columns per view.",
                    url=self.url,
                    selector="div[role=grid] columnheader",
                )
            headers = []
            for cell in cells:
                # Headers carry a long and a short label ("Change %"/"Chg %").
                label = require(
                    cell.find(class_="fv-table_header-label"),
                    self.url,
                    "div[role=columnheader] .fv-table_header-label",
                )
                text = label.get_text(strip=True)
                headers.append(LEGACY_LABELS.get(text, text))
            return headers
        table = self._screener_table(soup)
        rows = table.findAll("tr")
        table_headers = [i.text.strip() for i in rows[0].findAll("th")][1:]
        return table_headers

    def _parse_rows(self, soup: Any) -> list[list[Any]]:
        data = self._ssr_data(soup)
        if data is not None:
            grid = self._screener_grid(soup)
            rows = grid.find_all(attrs={"role": "row", "data-row-key": True})
            # The island lists every row of the page; fewer rendered grid rows
            # means the grid virtualized some away.
            expected = data.get("rows")
            if isinstance(expected, list) and len(rows) < len(expected):
                raise FinvizParseError(
                    f"Screener grid at {self.url} rendered {len(rows)} of "
                    f"{len(expected)} rows. Finviz markup may have changed "
                    "(Drift).",
                    url=self.url,
                    selector="div[role=row][data-row-key]",
                )
            return [self._grid_cells(row, "gridcell") for row in rows]
        table = self._screener_table(soup)
        return [row.find_all("td")[1:] for row in table.find_all("tr")[1:]]

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
        rows = self._parse_rows(soup)
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
