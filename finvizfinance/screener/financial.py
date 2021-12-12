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
        """initiate module"""
        self.BASE_URL = (
            "https://finviz.com/screener.ashx?v=161{signal}{filter}&ft=4{ticker}"
        )
        self.url = self.BASE_URL.format(signal="", filter="", ticker="")
        Overview._load_setting(self)
