"""
.. module:: screen.valuation
   :synopsis: screen valuation table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
from finvizfinance.screener.overview import Overview


class Valuation(Overview):
    """Valuation inherit from overview module.
    Getting information from the finviz screener valuation page.
    """

    v_page = 121
