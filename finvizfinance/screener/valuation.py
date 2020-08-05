from finvizfinance.screener.overview import Overview
"""
.. module:: screen.valuation
   :synopsis: screen valuation table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

class Valuation(Overview):
    """Valuation inherit from overview module.
        Getting information from the finviz screener valuation page.
    """
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=121{signal}{filter}&ft=4{ticker}'
        self.NUMBER_COL = ['Market Cap', 'P/E', 'Fwd P/E', 'PEG', 'P/S', 'P/B', 'P/C', \
                           'P/FCF', 'EPS this Y', 'EPS next Y', 'EPS past 5Y', 'EPS next 5Y', \
                           'Sales past 5Y', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(signal='', filter='', ticker='')
        Overview._loadSetting(self)