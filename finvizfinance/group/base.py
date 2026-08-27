"""
.. module:: group.base
   :synopsis: group base module.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

import pandas as pd

from finvizfinance.constants import group_dict, group_order_dict
from finvizfinance.util import scrap_group_table, validate_choice, web_scrap


class Base:
    """Base
    Getting information from the finviz group page.
    """

    v_page: int | None = None
    url = "https://finviz.com/groups.ashx"
    request_params: dict = {}

    def __init__(self) -> None:
        """initiate module"""
        self.request_params = {
            "v": self.v_page,
        }

    def _parse_columns(self, columns: list | None) -> None:
        return

    def screener_view(
        self, group: str = "Sector", order: str = "Name", columns: list | None = None
    ) -> pd.DataFrame:
        """Get screener table.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.
            columns(list): columns of your choice. Default index: None
        Returns:
            df(pandas.DataFrame): group information table.
        """
        validate_choice(group, group_dict, "group")
        validate_choice(order, group_order_dict, "order")

        self.request_params = {
            **self.request_params,
            **group_dict[group],
            "o": group_order_dict[order],
        }
        self._parse_columns(columns)

        soup = web_scrap(self.url, self.request_params)
        return scrap_group_table(soup, self.url)
