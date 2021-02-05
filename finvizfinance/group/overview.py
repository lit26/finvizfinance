from finvizfinance.util import webScrap, numberCovert
import pandas as pd
"""
.. module:: group.overview
   :synopsis: group overview table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>

"""


class Overview:
    """Overview
    Getting information from the finviz group overview page.
    """
    def __init__(self):
        """initiate module"""
        self.BASE_URL = 'https://finviz.com/groups.ashx?{group}&v=110'
        self.url = self.BASE_URL.format(group='g=sector')
        self._loadSetting()

    def _loadSetting(self):
        """load all the groups."""
        soup = webScrap(self.url)
        selects = soup.findAll('select')

        # group
        options = selects[0].findAll('option')
        key = [i.text for i in options]
        value = []
        for option in options:
            temp = option['value'].split('?')[1].split('&')
            if len(temp) == 4:
                temp = '&'.join(temp[:2])
            else:
                temp = temp[0]
            value.append(temp)
        self.group_dict = dict(zip(key, value))

        # order
        options = selects[1].findAll('option')
        key = [i.text for i in options]
        value = [i['value'].split('&')[-1] for i in options]
        self.order_dict = dict(zip(key, value))

    def getGroup(self):
        """Get groups.

        Returns:
            groups(list): all the available groups.
        """
        return list(self.group_dict.keys())

    def getOrders(self):
        """Get orders.

        Returns:
            orders(list): all the available orders.
        """
        return list(self.order_dict.keys())

    def ScreenerView(self, group='Sector', order='Name'):
        """Get screener table.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.

        Returns:
            df(pandas.DataFrame): group information table.
        """
        if group not in self.group_dict:
            raise ValueError()
        if order not in self.order_dict:
            raise ValueError()
        self.url = self.BASE_URL.format(group=self.group_dict[group])+'&'+self.order_dict[order]

        soup = webScrap(self.url)
        table = soup.findAll('table')[5]
        rows = table.findAll('tr')
        table_header = [i.text for i in rows[0].findAll('td')][1:]
        df = pd.DataFrame([], columns=table_header)
        rows = rows[1:]
        num_col_index = [i for i in range(2, len(table_header))]
        for row in rows:
            cols = row.findAll('td')[1:]
            info_dict = {}
            for i, col in enumerate(cols):
                # check if the col is number
                if i not in num_col_index:
                    info_dict[table_header[i]] = col.text
                else:
                    info_dict[table_header[i]] = numberCovert(col.text)

            df = df.append(info_dict, ignore_index=True)
        return df
