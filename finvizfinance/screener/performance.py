from finvizfinance.screener.overview import Overview

"""
.. module:: screen.performance
   :synopsis: screen performance table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

SCREENER_TABLE_INDEX = 21


class Performance(Overview):
    """Performance inherit from overview module.
    Getting information from the finviz screener performance page.

    Args:
        screener_table_index(int): table index of the stock screener. change only if change on finviz side.

    """

    def __init__(self, screener_table_index=SCREENER_TABLE_INDEX):
        """initiate module"""
        self._screener_table_index = screener_table_index
        self.BASE_URL = (
            "https://finviz.com/screener.ashx?v=141{signal}{filter}&ft=4{ticker}"
        )
        self.url = self.BASE_URL.format(signal="", filter="", ticker="")
        Overview._load_setting(self)
