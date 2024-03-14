"""
.. module:: screen.performance
   :synopsis: screen performance table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.screener.base import Base


class Performance(Base):
    """Performance inherit from overview module.
    Getting information from the finviz screener performance page.
    """

    v_page = 141
