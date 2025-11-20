"""
.. module:: screener.ownership
   :synopsis: screen ownership table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.screener.base import create_screener

Ownership = create_screener(
    v_page=131,
    class_name="Ownership",
    doc_string="""Ownership
    Getting information from the finviz screener ownership page.
    """,
)
