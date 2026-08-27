"""
.. module:: insider
   :synopsis: insider table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

import pandas as pd
from finvizfinance.util import web_scrap, number_convert, find_table_by_headers

INSIDER_URL = "https://finviz.com/insidertrading"

OPTION_QUERY = {
    "latest": "",
    "latest buys": "?tc=1",
    "latest sales": "?tc=2",
    "top week": "?or=-10&tv=100000&tc=7&o=-transactionValue",
    "top week buys": "?or=-10&tv=100000&tc=1&o=-transactionValue",
    "top week sales": "?or=-10&tv=100000&tc=2&o=-transactionValue",
    "top owner trade": "?or=10&tv=1000000&tc=7&o=-transactionValue",
    "top owner buys": "?or=10&tv=1000000&tc=1&o=-transactionValue",
    "top owner sales": "?or=10&tv=1000000&tc=2&o=-transactionValue",
}


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
        if option in OPTION_QUERY:
            self.url = INSIDER_URL + OPTION_QUERY[option]
        elif option.isdigit():
            self.url = INSIDER_URL + "?oc=" + option + "&tc=7"
        else:
            raise ValueError(
                "Invalid option '{}'. Possible options: {}".format(
                    option, list(OPTION_QUERY.keys()) + ["insider_id (digits)"]
                )
            )
        self.soup = web_scrap(self.url)
        self.df = None

    def get_insider(self):
        """Get insider information table.

        Returns:
            df(pandas.DataFrame): insider information table
        """
        # Match the insider table by its header text rather than a fixed
        # positional index, so it survives finviz reordering tables. A missing
        # table raises FinvizParseError, never a cryptic IndexError.
        insider_trader = find_table_by_headers(
            self.soup,
            ["Ticker", "Owner", "Transaction"],
            self.url,
            "insider trading table",
        )
        rows = insider_trader.find_all("tr")
        table_header = [i.text.strip() for i in rows[0].find_all("th")] + [
            "SEC Form 4 Link"
        ]
        frame = []
        rows = rows[1:]
        num_col = ["Cost", "#Shares", "Value ($)", "#Shares Total"]
        num_col_index = [table_header.index(i) for i in table_header if i in num_col]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            info_dict = {}
            for i, col in enumerate(cols):
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                else:
                    info_dict[table_header[i]] = number_convert(col.text)
            link = cols[-1].find("a")
            info_dict["SEC Form 4 Link"] = link.attrs["href"] if link else None
            frame.append(info_dict)
        df = pd.DataFrame(frame)
        self.df = df
        return df
