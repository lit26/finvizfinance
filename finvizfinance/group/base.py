"""
.. module:: group.base
   :synopsis: group base module.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

import pandas as pd
from finvizfinance.util import web_scrap, number_covert
from finvizfinance.constants import group_dict, group_order_dict


class Base:
    """Base
    Getting information from the finviz group page.
    """

    v_page = None
    url = "https://finviz.com/groups.ashx"
    request_params = {}

    def __init__(self, v_page=None):
        """initiate module

        Args:
            v_page(int): page version number (optional, uses class attribute if not provided)
        """
        if v_page is not None:
            self.v_page = v_page
        self.request_params = {
            "v": self.v_page,
        }

    def _parse_columns(self, columns):
        return

    def screener_view(self, group="Sector", order="Name", columns=None):
        """Get screener table.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.
            columns(list): columns of your choice. Default index: None
        Returns:
            df(pandas.DataFrame): group information table.
        """
        if group not in group_dict:
            group_keys = list(group_dict.keys())
            raise ValueError(
                "Invalid group parameter '{}'. Possible parameter input: {}".format(
                    group, group_keys
                )
            )
        if order not in group_order_dict:
            order_keys = list(group_order_dict.keys())
            raise ValueError(
                "Invalid order parameter '{}'. Possible parameter input: {}".format(
                    order, order_keys
                )
            )

        self.request_params = {
            **self.request_params,
            **group_dict[group],
            "o": group_order_dict[order],
        }
        self._parse_columns(columns)

        soup = web_scrap(self.url, self.request_params)
        table = soup.find("table", class_="groups_table")
        rows = table.find_all("tr")
        table_header = [i.text.strip() for i in rows[0].find_all("th")][1:]
        frame = []
        rows = rows[1:]
        num_col_index = list(range(2, len(table_header)))
        for row in rows:
            cols = row.find_all("td")[1:]
            info_dict = {}
            for i, col in enumerate(cols):
                # check if the col is number
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                else:
                    info_dict[table_header[i]] = number_covert(col.text)

            frame.append(info_dict)
        return pd.DataFrame(frame)


def create_group(v_page, class_name, doc_string):
    """Factory function to create a group class with a specific v_page value.

    Args:
        v_page(int): page version number
        class_name(str): name of the class
        doc_string(str): documentation string for the class

    Returns:
        class: A new class inheriting from Base with the specified v_page
    """
    return type(
        class_name,
        (Base,),
        {
            "v_page": v_page,
            "__doc__": doc_string,
        },
    )
