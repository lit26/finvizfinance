from finvizfinance.group.overview import Overview
from finvizfinance.util import webScrap, imageScrap

"""
.. module:: group.spectrum
   :synopsis: group spectrum image.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


class Spectrum(Overview):
    """Spectrum inherit from overview module.
    Getting information from the finviz group spectrum page.
    """
    def __init__(self):
        """initiate module
        """
        self.BASE_URL = 'https://finviz.com/groups.ashx?{group}&v=310'
        self.url = self.BASE_URL.format(group='g=sector')
        Overview._loadSetting(self)

    def ScreenerView(self, group='Sector', order='Name', out_dir=''):
        """Get screener table.

        Args:
            group(str): choice of group option.
            order(str): sort the table by the choice of order.
        """
        if group not in self.group_dict:
            raise ValueError()
        if order not in self.order_dict:
            raise ValueError()
        self.url = self.BASE_URL.format(group=self.group_dict[group])+'&'+self.order_dict[order]

        soup = webScrap(self.url)
        url = 'https://finviz.com/' + soup.findAll('img')[5]['src']
        imageScrap(url, group, '')