"""
.. module:: group.overview
   :synopsis: group overview table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
import pandas as pd
from finvizfinance.util import web_scrap, number_covert


class Overview:
    """Overview
    Getting information from the finviz group overview page.
    """

    v_page = 110

    def __init__(self):
        """initiate module"""
        self.BASE_URL = "https://finviz.com/groups.ashx?{group}&v={v_page}"
        self.url = self.BASE_URL.format(group="g=sector", v_page=self.v_page)
        self._load_setting()

    def _load_setting(self):
        """load all the groups."""
        soup = web_scrap(self.url)
        selects = soup.findAll("select")

        # group
        options = selects[0].findAll("option")
        key = [i.text.strip() for i in options]
        value = []
        for option in options:
            temp = option["value"].split("?")[1].split("&")
            if len(temp) == 4:
                temp = "&".join(temp[:2])
            else:
                temp = temp[0]
            value.append(temp)
        self.group_dict = dict(zip(key, value))

        # order
        options = selects[1].findAll("option")
        key = [i.text.strip() for i in options]
        value = [i["value"].split("&")[-1] for i in options]
        self.order_dict = dict(zip(key, value))

    def get_group(self):
        """Get groups.

        Returns:
            groups(list): all the available groups.
        """
        return list(self.group_dict.keys())

    def get_orders(self):
        """Get orders.

        Returns:
            orders(list): all the available orders.
        """
        return list(self.order_dict.keys())

    def screener_view(self, group="Sector", order="Name"):
        """Get screener table.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.

        Returns:
            df(pandas.DataFrame): group information table.
        """
        if group not in self.group_dict:
            group_keys = list(self.group_dict.keys())
            raise ValueError(
                "Invalid group parameter '{}'. Possible parameter input: {}".format(
                    group, group_keys
                )
            )
        if order not in self.order_dict:
            order_keys = list(self.order_dict.keys())
            raise ValueError(
                "Invalid order parameter '{}'. Possible parameter input: {}".format(
                    order, order_keys
                )
            )
        self.url = (
            self.BASE_URL.format(group=self.group_dict[group], v_page=self.v_page)
            + "&"
            + self.order_dict[order]
        )

        soup = web_scrap(self.url)
        table = soup.find("table", class_="table-light")
        rows = table.findAll("tr")
        table_header = [i.text.strip() for i in rows[0].findAll("td")][1:]
        frame = []
        rows = rows[1:]
        num_col_index = list(range(2, len(table_header)))
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
        return pd.DataFrame(frame)
