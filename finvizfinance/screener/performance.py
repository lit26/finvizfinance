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
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=141{filter}&ft=4'
        self.NUMBER_COL = ['Perf Week', 'Perf Month', 'Perf Quart', 'Perf Half',
                           'Perf Year', 'Perf YTD', 'Volatility W', 'Volatility M',
                           'Recom', 'Avg Volume', 'Rel Volume', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(filter='')
        Overview._loadSetting(self)