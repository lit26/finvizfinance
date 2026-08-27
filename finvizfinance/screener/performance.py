"""
.. module:: screener.performance
   :synopsis: screen performance table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

from finvizfinance.screener.base import Base


class Performance(Base):
    """Performance
    Getting information from the finviz screener performance page.
    """

    v_page = 141
