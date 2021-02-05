from finvizfinance.group.overview import Overview
"""
.. module:: group.valuation
   :synopsis: group valuation table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


class Valuation(Overview):
    """Valuation inherit from overview module.
    Getting information from the finviz group valuation page.
    """
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/groups.ashx?{group}&v=120'
        self.url = self.BASE_URL.format(group='g=sector')
        Overview._loadSetting(self)