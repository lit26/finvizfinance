"""
.. module:: screener.ownership
   :synopsis: screen ownership table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.screener.base import Base


class Ownership(Base):
    """Ownership
    Getting information from the finviz screener ownership page.
    """

    v_page = 131
