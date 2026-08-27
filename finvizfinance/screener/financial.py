"""
.. module:: screener.financial
   :synopsis: screen financial table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

from finvizfinance.screener.base import Base


class Financial(Base):
    """Financial
    Getting information from the finviz screener financial page.
    """

    v_page = 161
