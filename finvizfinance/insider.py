import pandas as pd
from finvizfinance.util import web_scrap, number_covert

"""
.. module:: insider
   :synopsis: insider table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

INSIDER_URL = "https://finviz.com/insidertrading.ashx"


class Insider:
    """Insider
    Getting information from the finviz insider page.

    Args:
        option (str): choose a option (latest, latest buys, latest sales, top week,
                      top week buys, top week sales, top owner trade, top owner buys,
                      top owner sales, insider_id)
    """

    def __init__(self, option="latest"):
        """initiate module"""
        if option == "latest":
            self.soup = web_scrap(INSIDER_URL)
        elif option == "latest buys":
            self.soup = web_scrap(INSIDER_URL + "?tc=1")
        elif option == "latest sales":
            self.soup = web_scrap(INSIDER_URL + "?tc=2")
        elif option == "top week":
            self.soup = web_scrap(
                INSIDER_URL + "?or=-10&tv=100000&tc=7&o=-transactionValue"
            )
        elif option == "top week buys":
            self.soup = web_scrap(
                INSIDER_URL + "?or=-10&tv=100000&tc=1&o=-transactionValue"
            )
        elif option == "top week sales":
            self.soup = web_scrap(
                INSIDER_URL + "?or=-10&tv=100000&tc=2&o=-transactionValue"
            )
        elif option == "top owner trade":
            self.soup = web_scrap(
                INSIDER_URL + "?or=10&tv=1000000&tc=7&o=-transactionValue"
            )
        elif option == "top owner buys":
            self.soup = web_scrap(
                INSIDER_URL + "?or=10&tv=1000000&tc=1&o=-transactionValue"
            )
        elif option == "top owner sales":
            self.soup = web_scrap(
                INSIDER_URL + "?or=10&tv=1000000&tc=2&o=-transactionValue"
            )
        elif option.isdigit():
            self.soup = web_scrap(INSIDER_URL + "?oc=" + option + "&tc=7")
        self.df = None

    def get_insider(self):
        """Get insider information table.

        Returns:
            df(pandas.DataFrame): insider information table
        """
        insider_trader = self.soup.findAll("table")[5]
        rows = insider_trader.findAll("tr")
        table_header = [i.text.strip() for i in rows[0].findAll("td")] + [
            "SEC Form 4 Link"
        ]
        df = pd.DataFrame([], columns=table_header)
        rows = rows[1:]
        num_col = ["Cost", "#Shares", "Value ($)", "#Shares Total"]
        num_col_index = [table_header.index(i) for i in table_header if i in num_col]
        for row in rows:
            cols = row.findAll("td")
            info_dict = {}
            for i, col in enumerate(cols):
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                    if i == len(cols) - 1:
                        info_dict["SEC Form 4 Link"] = col.find("a").attrs["href"]
                else:
                    info_dict[table_header[i]] = number_covert(col.text)
                info_dict["SEC Form 4 Link"] = cols[-1].find("a").attrs["href"]
            df = df.append(info_dict, ignore_index=True)
        self.df = df
        return df
