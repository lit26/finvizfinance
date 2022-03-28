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
        """initiate module"""
        self.BASE_URL = (
            "https://finviz.com/screener.ashx?v=121{signal}{filter}&ft=4{ticker}"
        )
        self.url = self.BASE_URL.format(signal="", filter="", ticker="")
        Overview._load_setting(self)
