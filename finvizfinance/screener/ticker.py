"""
.. module:: screener.ticker
   :synopsis: screen ticker table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

import logging
from time import sleep
from typing import Any

from finvizfinance.constants import order_dict
from finvizfinance.screener.base import Base
from finvizfinance.util import (
    progress_bar,
    require,
    validate_choice,
    web_scrap,
)

logger = logging.getLogger(__name__)


class Ticker(Base):
    """Financial
    Getting information from the finviz screener ticker page.
    """

    v_page = 411

    def _screener_helper(
        self, i: int, page: int, soup: Any, tickers: list[str], limit: int
    ) -> list[str]:
        td = require(
            soup.find("td", class_="screener-tickers"),
            self.url,
            "td.screener-tickers",
        )
        page_tickers = td.find_all("span")
        if i == page - 1:
            page_tickers = page_tickers[: ((limit - 1) % 1000 + 1)]
        for span in page_tickers:
            parts = span.text.split("\xa0")
            # Cells normally read "<rank>\xa0<TICKER>"; fall back to the whole
            # text when the NBSP-separated rank is absent (avoids IndexError).
            tickers.append(parts[1] if len(parts) > 1 else parts[0])
        return tickers

    def screener_view(  # type: ignore[override]  # public API intentionally differs from Base
        self,
        order: str = "Ticker",
        limit: int = -1,
        verbose: int = 1,
        ascend: bool = True,
        sleep_sec: int = 1,
    ) -> list[str] | None:
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
        validate_choice(order, order_dict, "order")
        self.request_params["o"] = ("" if ascend else "-") + order_dict[order]
        soup = web_scrap(self.url, self.request_params)
        page = self._get_page(soup)
        if page == 0:
            logger.warning("No ticker found.")
            return None

        if limit != -1 and page > (limit - 1) // 1000 + 1:
            page = (limit - 1) // 1000 + 1

        if verbose == 1:
            progress_bar(1, page)

        tickers: list[str] = []
        tickers = self._screener_helper(0, page, soup, tickers, limit)

        for i in range(1, page):
            sleep(sleep_sec)  # Adding sleep
            if verbose == 1:
                progress_bar(i + 1, page)
            self.request_params["r"] = i * 1000 + 1
            soup = web_scrap(self.url, self.request_params)
            tickers = self._screener_helper(i, page, soup, tickers, limit)
        return tickers
