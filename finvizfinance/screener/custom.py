import warnings
import pandas as pd
from finvizfinance.screener.overview import Overview
from finvizfinance.util import web_scrap, progress_bar, NUMBER_COL

"""
.. module:: screen.custom
   :synopsis: screen custom table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

COLUMNS = {
    0: "No.",
    1: "Ticker",
    2: "Company",
    3: "Sector",
    4: "Industry",
    5: "Country",
    6: "Market Cap.",
    7: "P/E",
    8: "Forward P/E",
    9: "PEG",
    10: "P/S",
    11: "P/B",
    12: "P/Cash",
    13: "P/Free Cash Flow",
    14: "Dividend Yield",
    15: "Payout Ratio",
    16: "EPS",
    17: "EPS growth this year",
    18: "EPS growth next year",
    19: "EPS growth past 5 years",
    20: "EPS growth next 5 years",
    21: "Sales growth past 5 years",
    22: "EPS growth qtr over qtr",
    23: "Sales growth qtr over qtr",
    24: "Shares Outstanding",
    25: "Shares Float",
    26: "Insider Ownership",
    27: "Insider Transactions",
    28: "Institutional Ownership",
    29: "Institutional Transactions",
    30: "Float Short",
    31: "Short Ratio",
    32: "Return on Assets",
    33: "Return on Equity",
    34: "Return on Investments",
    35: "Current Ratio",
    36: "Quick Ratio",
    37: "Long Term Debt/Equity",
    38: "Total Debt/Equity",
    39: "Gross Margin",
    40: "Operating Margin",
    41: "Net Profit Margin",
    42: "Performance (Week)",
    43: "Performance (Month)",
    44: "Performance (Quarter)",
    45: "Performance (Half Year)",
    46: "Performance (Year)",
    47: "Performance (YearToDate)",
    48: "Beta",
    49: "Average True Range",
    50: "Volatility (Week)",
    51: "Volatility (Month)",
    52: "20-Day Simple Moving Average",
    53: "50-Day Simple Moving Average",
    54: "200-Day Simple Moving Average",
    55: "50-Day High",
    56: "50-Day Low",
    57: "52-Week High",
    58: "52-Week Low",
    59: "RSI",
    60: "Change from Open",
    61: "Gap",
    62: "Analyst Recom.",
    63: "Average Volume",
    64: "Relative Volume",
    65: "Price",
    66: "Change",
    67: "Volume",
    68: "Earnings Date",
    69: "Target Price",
    70: "IPO Date",
}


class Custom(Overview):
    """Custom inherit from overview module.
    Getting information from the finviz screener custom page.
    """

    def __init__(self):
        """initiate module"""
        self.BASE_URL = (
            "https://finviz.com/screener.ashx?v=151{signal}{filter}&ft=4{ticker}"
        )
        self.url = self.BASE_URL.format(signal="", filter="", ticker="")
        Overview._load_setting(self)

    def get_columns(self):
        """Get information about the columns

        Returns:
            columns(dict): return the index and column name.
        """
        return COLUMNS

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
        columns=[0, 1, 2, 3, 4, 5, 6, 7, 65, 66, 67],
    ):
        """Get screener table.

        Args:
            order(str): sort the table by the choice of order.
            limit(int): set the top k rows of the screener.
            select_page(int): set the page of the screener.
            verbose(int): choice of visual the progress. 1 for visualize progress.
            ascend(bool): if True, the order is ascending.
            columns(list): columns of your choice. Default index: 0,1,2,3,4,5,6,7,65,66,67.
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
        columns = [str(i) for i in columns]
        url += "&c=" + ",".join(columns)
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

        table = soup.findAll("table")[18]
        rows = table.findAll("tr")
        table_header = [i.text for i in rows[0].findAll("td")][1:]
        num_col_index = [table_header.index(i) for i in table_header if i in NUMBER_COL]
        df = pd.DataFrame([], columns=table_header)
        if not select_page or select_page == 1:
            df = self._screener_helper(
                0, page, rows, df, num_col_index, table_header, limit
            )

        if select_page != 1:
            for i in range(start_page, end_page):
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
                url += "&c=" + ",".join(columns)
                soup = web_scrap(url)
                table = soup.findAll("table")[18]
                rows = table.findAll("tr")
                df = self._screener_helper(
                    i, page, rows, df, num_col_index, table_header, limit
                )
        return df
