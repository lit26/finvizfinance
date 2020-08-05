from finvizfinance.screener.overview import Overview
"""
.. module:: screen.financial
   :synopsis: screen financial table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

class Financial(Overview):
    """Financial inherit from overview module.
    Getting information from the finviz screener financial page.
    """
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=161{signal}{filter}&ft=4{ticker}'
        self.NUMBER_COL = ['Market Cap', 'Dividend', 'ROA', 'ROE', 'ROI',
                           'Curr R', 'Quick R', 'LTDebt/Eq', 'Debt/Eq', 'Gross M',
                           'Oper M', 'Profit M', 'Price', 'Change', 'Volume']
        self.url = self.BASE_URL.format(signal='', filter='', ticker='')
        Overview._loadSetting(self)