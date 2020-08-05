from finvizfinance.screener.overview import Overview
"""
.. module:: screen.technical
   :synopsis: screen technical table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

class Technical(Overview):
    """Technical inherit from overview module.
    Getting information from the finviz screener technical page.
    """
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=171{signal}{filter}&ft=4{ticker}'
        self.NUMBER_COL = ['Beta', 'ATR', 'SMA20', 'SMA50', 'SMA200', '52W High',
                           '52W Low', 'RSI', 'Price', 'Change', 'from Open', 'Gap', 'Volume']
        self.url = self.BASE_URL.format(signal='', filter='', ticker='')
        Overview._loadSetting(self)