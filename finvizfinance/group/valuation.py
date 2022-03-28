from finvizfinance.group.overview import Overview

"""
.. module:: group.valuation
   :synopsis: group valuation table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
SCREENER_TABLE_INDEX = 7


class Valuation(Overview):
    """Valuation inherit from overview module.
    Getting information from the finviz group valuation page.
    Args:
        screener_table_index(int): table index of the stock screener. change only if change on finviz side.

    """

    def __init__(self, screener_table_index=SCREENER_TABLE_INDEX):
        """initiate module"""
        self._screener_table_index = screener_table_index
        self.BASE_URL = "https://finviz.com/groups.ashx?{group}&v=120"
        self.url = self.BASE_URL.format(group="g=sector")
        Overview._load_setting(self)
