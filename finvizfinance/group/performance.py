"""
.. module:: group.performance
   :synopsis: group performance table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

from finvizfinance.group.base import Base


class Performance(Base):
    """Performance
    Getting information from the finviz group performance page.
    """

    v_page = 140
