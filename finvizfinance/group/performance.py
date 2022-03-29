"""
.. module:: group.performance
   :synopsis: group performance table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
from finvizfinance.group.overview import Overview


class Performance(Overview):
    """Performance inherit from overview module.
    Getting information from the finviz group performance page.
    """

    v_page = 140
