"""
.. module:: screener.valuation
   :synopsis: screen valuation table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.screener.base import Base


class Valuation(Base):
    """Valuation
    Getting information from the finviz screener valuation page.
    """

    v_page = 121
