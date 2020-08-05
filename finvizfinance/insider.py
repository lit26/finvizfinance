from finvizfinance.util import webScrap, numberCovert
import pandas as pd
"""
.. module:: insider
   :synopsis: insider table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

INSIDER_URL = 'https://finviz.com/insidertrading.ashx'

class Insider:
    """Insider
    Getting information from the finviz insider page.

    Args:
        option (str): choose a option (latest, top week, top owner trade, insider_id)
    """
    def __init__(self, option='latest'):
        """initiate module
        """
        if option == 'latest':
            self.soup = webScrap(INSIDER_URL)
        elif option == 'top week':
            self.soup = webScrap(INSIDER_URL+'?or=-10&tv=100000&tc=7&o=-transactionValue')
        elif option == 'top owner trade':
            self.soup = webScrap(INSIDER_URL+'?or=10&tv=1000000&tc=7&o=-transactionValue')
        elif option.isdigit():
            self.soup = webScrap(INSIDER_URL+'?oc='+option+'&tc=7')
        self.df = None

    def getInsider(self):
        """Get insider information table.

        Returns:
            df(pandas.DataFrame): insider information table
        """
        insider_trader = self.soup.findAll('table')[5]
        rows = insider_trader.findAll('tr')
        table_header = [i.text.strip() for i in rows[0].findAll('td')]
        df = pd.DataFrame([], columns=table_header)
        rows = rows[1:]
        num_col = ['Cost', '#Shares', 'Value ($)', '#Shares Total']
        num_col_index = [table_header.index(i) for i in table_header if i in num_col]
        for row in rows:
            cols = row.findAll('td')
            info_dict = {}
            for i, col in enumerate(cols):
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                else:
                    info_dict[table_header[i]] = numberCovert(col.text)
            df = df.append(info_dict, ignore_index=True)
        self.df = df
        return df