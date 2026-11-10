"""
.. module:: screener.custom
   :synopsis: screen custom table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

from time import sleep

import pandas as pd

from finvizfinance.screener.base import Base

# The redesigned screener grid renders only the columns that fit the server's
# assumed viewport (38 of 71 in a probe on 2026-10-24). Wider views are fetched
# in chunks of at most this many columns, counting "No." and Ticker.
MAX_COLUMNS = 30


class Custom(Base):
    """Custom
    Getting information from the finviz screener custom page.
    """

    v_page = 151

    def _parse_columns(self, columns: list | None) -> None:
        if not columns:
            return
        if 0 in columns:
            columns.remove(0)
        columns.insert(0, 0)
        columns = [str(i) for i in columns]
        self.request_params["c"] = ",".join(columns)

    def screener_view(
        self,
        order: str = "Ticker",
        limit: int = -1,
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
            columns(list): columns of your choice. Default index: 0,1,2,3,4,5,6,7,65,66,67.
                Views wider than MAX_COLUMNS are fetched as several narrower
                ones joined on Ticker, which then comes first.
            sleep_sec(int): sleep seconds for fetching each page.
        Returns:
            df(pandas.DataFrame): screener information table
        """
        if columns is None:
            columns = [0, 1, 2, 3, 4, 5, 6, 7, 65, 66, 67]
        # "No." (0) is always prepended by _parse_columns; copy so the caller's
        # list is never mutated.
        columns = [c for c in columns if c != 0]
        if len(columns) + 1 <= MAX_COLUMNS:
            return Base.screener_view(
                self, order, limit, select_page, verbose, ascend, columns, sleep_sec
            )
        return self._chunked_view(
            columns, order, limit, select_page, verbose, ascend, sleep_sec
        )

    def _chunked_view(
        self,
        columns: list,
        order: str,
        limit: int,
        select_page: int | None,
        verbose: int,
        ascend: bool,
        sleep_sec: int,
    ) -> pd.DataFrame:
        """Fetch a wide view as several narrower ones joined on Ticker.

        The result holds Ticker first (only if requested), then the other
        columns in the order given.
        """
        others = [c for c in columns if c != 1]
        step = MAX_COLUMNS - 2  # every chunk also carries "No." and Ticker
        params = dict(self.request_params)
        frames = []
        for start in range(0, len(others), step):
            if start:
                sleep(sleep_sec)
            # Base.screener_view resets request_params (filters included) when
            # it finishes, so each chunk starts from the caller's settings.
            self.request_params = dict(params)
            df = Base.screener_view(
                self,
                order,
                limit,
                select_page,
                verbose,
                ascend,
                [1, *others[start : start + step]],
                sleep_sec,
            )
            if df is None:
                return None
            frames.append(df)

        tickers = frames[0].iloc[:, 0]
        parts = [tickers]
        for df in frames:
            body = df.iloc[:, 1:]
            if not df.iloc[:, 0].equals(tickers):
                # Rows moved between requests (e.g. sorted by a live price):
                # align on the symbol rather than position.
                body = body.set_index(df.iloc[:, 0]).reindex(tickers)
                body = body.reset_index(drop=True)
            parts.append(body)
        result = pd.concat(parts, axis=1)
        return result if 1 in columns else result.iloc[:, 1:]
