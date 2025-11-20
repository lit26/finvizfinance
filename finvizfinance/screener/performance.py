"""
.. module:: screener.performance
   :synopsis: screen performance table.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from finvizfinance.screener.base import create_screener

Performance = create_screener(
    v_page=141,
    class_name="Performance",
    doc_string="""Performance
    Getting information from the finviz screener performance page.
    """,
)
