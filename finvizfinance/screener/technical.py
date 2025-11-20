"""
.. module:: screener.technical
   :synopsis: screen technical table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.screener.base import create_screener

Technical = create_screener(
    v_page=171,
    class_name="Technical",
    doc_string="""Technical
    Getting information from the finviz screener technical page.
    """,
)
