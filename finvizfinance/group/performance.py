from finvizfinance.group.overview import Overview
"""
.. module:: group.performance
   :synopsis: group performance table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


class Performance(Overview):
    """Performance inherit from overview module.
    Getting information from the finviz group performance page.
    """
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/groups.ashx?{group}&v=140'
        self.url = self.BASE_URL.format(group='g=sector')
        Overview._loadSetting(self)