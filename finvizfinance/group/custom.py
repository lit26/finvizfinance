"""
.. module:: group.custom
   :synopsis: group custom table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
import pandas as pd
from finvizfinance.util import web_scrap, number_covert
from finvizfinance.group.overview import Overview


COLUMNS = {
    0: "No.",
    1: "Name",
    2: "Market Cap.",
    3: "P/E",
    4: "Forward P/E",
    5: "PEG",
    6: "P/S",
    7: "P/B",
    8: "P/Cash",
    9: "P/Free Cash Flow",
    10: "Dividend Yield",
    11: "EPS growth past 5 years",
    12: "EPS growth next 5 years",
    13: "Sales growth past 5 years",
    14: "Shares Float",
    15: "Performance (Week)",
    16: "Performance (Month)",
    17: "Performance (Quarter)",
    18: "Performance (Half Year)",
    19: "Performance (Year)",
    20: "Performance (YearToDate)",
    21: "Analyst Recom.",
    22: "Average Volume",
    23: "Relative Volume",
    24: "Change",
    25: "Volume",
    26: "Number of Stocks",
}


class Custom(Overview):
    """Custom inherit from overview module.
    Getting information from the finviz group custom page.
    """

    v_page = 152

    def get_columns(self):
        """Get information about the columns

        Returns:
            columns(dict): return the index and column name.
        """
        return COLUMNS

    def screener_view(
        self, group="Sector", order="Name", columns=[0, 1, 2, 3, 10, 22, 24, 25, 26]
    ):
        """Get screener table.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.
            columns(list): columns of your choice. Default index: 0, 1, 2, 3, 10, 22, 24, 25, 26.
        Returns:
            df(pandas.DataFrame): group information table.
        """
        if group not in self.group_dict:
            raise ValueError()
        if order not in self.order_dict:
            raise ValueError()
        self.url = (
            self.BASE_URL.format(group=self.group_dict[group], v_page=self.v_page)
            + "&"
            + self.order_dict[order]
        )
        columns = [str(i) for i in columns]
        self.url += "&c=" + ",".join(columns)

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
