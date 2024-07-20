"""
.. module:: group.valuation
   :synopsis: group valuation table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.group.base import Base


class Valuation(Base):
    """Valuation
    Getting information from the finviz group valuation page.
    """

    v_page = 120
