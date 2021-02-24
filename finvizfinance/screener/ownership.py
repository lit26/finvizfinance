from finvizfinance.screener.overview import Overview
"""
.. module:: screen.ownership
   :synopsis: screen ownership table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


class Ownership(Overview):
    """Ownership inherit from overview module.
    Getting information from the finviz screener ownership page.
    """
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/screener.ashx?v=131{signal}{filter}&ft=4{ticker}'
        self.url = self.BASE_URL.format(signal='', filter='', ticker='')
        Overview._loadSetting(self)