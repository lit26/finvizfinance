"""
.. module:: screen.financial
   :synopsis: screen financial table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
from finvizfinance.screener.overview import Overview


class Financial(Overview):
    """Financial inherit from overview module.
    Getting information from the finviz screener financial page.
    """

    v_page = 161
