"""
.. module:: screener.valuation
   :synopsis: screen valuation table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.screener.base import create_screener

Valuation = create_screener(
    v_page=121,
    class_name="Valuation",
    doc_string="""Valuation
    Getting information from the finviz screener valuation page.
    """,
)
