"""
.. module:: screener.financial
   :synopsis: screen financial table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.screener.base import create_screener

Financial = create_screener(
    v_page=161,
    class_name="Financial",
    doc_string="""Financial
    Getting information from the finviz screener financial page.
    """,
)
