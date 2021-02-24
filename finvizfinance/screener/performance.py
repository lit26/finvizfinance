from finvizfinance.screener.overview import Overview
"""
.. module:: screen.performance
   :synopsis: screen performance table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


class Performance(Overview):
    """Performance inherit from overview module.
    Getting information from the finviz screener performance page.
    """
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=141{signal}{filter}&ft=4{ticker}'
        self.url = self.BASE_URL.format(signal='', filter='', ticker='')
        Overview._loadSetting(self)